package com.ebbill.mobile

import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.net.http.SslError
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.view.View
import android.webkit.JavascriptInterface
import android.webkit.PermissionRequest
import android.webkit.SslErrorHandler
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import java.util.Locale

class MainActivity : ComponentActivity() {
    private lateinit var webView: WebView
    private var pendingAudioPermissionRequest: PermissionRequest? = null
    private var textToSpeech: TextToSpeech? = null

    private val startUrl = BuildConfig.BASE_URL
    private val audioPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        val request = pendingAudioPermissionRequest
        pendingAudioPermissionRequest = null
        if (granted && request != null) {
            request.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
        } else {
            request?.deny()
        }
    }


    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.cacheMode = WebSettings.LOAD_DEFAULT
        webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
        webView.settings.builtInZoomControls = false
        webView.settings.displayZoomControls = false
        webView.addJavascriptInterface(VoiceBridge(), "AndroidVoice")

        textToSpeech = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                textToSpeech?.language = Locale.US
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onPermissionRequest(request: PermissionRequest) {
                if (request.resources.contains(PermissionRequest.RESOURCE_AUDIO_CAPTURE)) {
                    val hasAudioPermission = ContextCompat.checkSelfPermission(
                        this@MainActivity,
                        android.Manifest.permission.RECORD_AUDIO
                    ) == PackageManager.PERMISSION_GRANTED

                    if (hasAudioPermission) {
                        request.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
                    } else {
                        pendingAudioPermissionRequest = request
                        audioPermissionLauncher.launch(android.Manifest.permission.RECORD_AUDIO)
                    }
                } else {
                    request.deny()
                }
            }
        }
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                return false
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                webView.visibility = View.VISIBLE
            }

            override fun onReceivedSslError(
                view: WebView?,
                handler: SslErrorHandler,
                error: SslError?
            ) {
                if (BuildConfig.ALLOW_SELF_SIGNED_SSL) {
                    // Debug only: allow local adhoc certificates.
                    handler.proceed()
                } else {
                    handler.cancel()
                }
            }
        }

        if (savedInstanceState == null) {
            webView.loadUrl(startUrl)
        } else {
            webView.restoreState(savedInstanceState)
        }

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    finish()
                }
            }
        })
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    override fun onDestroy() {
        textToSpeech?.stop()
        textToSpeech?.shutdown()
        webView.destroy()
        super.onDestroy()
    }

    inner class VoiceBridge {
        @JavascriptInterface
        fun speak(message: String?) {
            val safe = message?.trim().orEmpty()
            if (safe.isEmpty()) return
            runOnUiThread {
                textToSpeech?.speak(safe, TextToSpeech.QUEUE_FLUSH, null, "jervis_reply")
            }
        }
    }
}
