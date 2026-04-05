package com.ebbill.mobile
import retrofit2.http.GET

interface ApiService {
    @GET("api/appliances")
    suspend fun getAppliances(): AppliancesResponse

    @GET("api/realtime/latest")
    suspend fun getRealtime(): RealtimeResponse
}
