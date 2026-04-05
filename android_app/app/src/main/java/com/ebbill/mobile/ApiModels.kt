package com.ebbill.mobile


data class Appliance(
    val id: String,
    val name: String,
    val icon: String,
    val data_types: List<String>
)

data class AppliancesResponse(
    val appliances: List<Appliance>
)

data class RealtimeResponse(
    val timestamp: String?,
    val power: Double,
    val today_energy: Double,
    val month_energy: Double,
    val today_cost: Double,
    val month_cost: Double
)
