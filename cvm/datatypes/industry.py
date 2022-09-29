from __future__ import annotations
from enum import IntEnum

__all__ = [
    'Industry'
]

class Industry(IntEnum):
    OIL_AND_GAS                                          = 1010
    PETROCHEMICAL_AND_RUBBER                             = 1020
    MINERAL_EXTRACTION                                   = 1030
    PULP_AND_PAPER                                       = 1040
    TEXTILE_AND_CLOTHING                                 = 1050
    METALLURGY_AND_STEELMAKING                           = 1060
    MACHINERY_EQUIPMENT_VEHICLE_AND_PARTS                = 1070
    PHARMACEUTICAL_AND_HYGIENE                           = 1080
    BEVERAGES_AND_TOBACCO                                = 1090
    PRINTERS_AND_PUBLISHERS                              = 1100
    CIVIL_CONSTRUCTION_BUILDING_AND_DECORATION_MATERIALS = 1110
    ELETRICITY                                           = 1120
    TELECOMMUNICATIONS                                   = 1130
    TRANSPORT_AND_LOGISTICS_SERVICES                     = 1140
    COMMUNICATION_AND_INFORMATION_TECHNOLOGY             = 1150
    SANITATION_WATER_AND_GAS_SERVICES                    = 1160
    MEDICAL_SERVICES                                     = 1170
    HOSTING_AND_TOURISM                                  = 1180
    WHOLESAIL_AND_RETAIL_COMMERCE                        = 1190
    FOREIGN_COMMERCE                                     = 1200
    AGRICULTURE                                          = 1210
    FOOD                                                 = 1220
    COOPERATIVES                                         = 1230
    BANKS                                                = 1240
    INSURANCE_AND_BROKERAGE_COMPANIES                    = 1250
    LEASING                                              = 1260
    PRIVATE_PENSION                                      = 1270
    FINANCIAL_INTERMEDIATION                             = 1280
    FACTORING                                            = 1290
    REAL_ESTATE_CREDIT                                   = 1300
    REFORESTATION                                        = 1310
    FISHING                                              = 1320
    PACKAGING                                            = 1330
    EDUCATION                                            = 1380
    SECURITIZATION_OF_RECEIVABLES                        = 1390
    TOYS_AND_RECREATIONAL                                = 1400
    STOCK_EXCHANGES                                      = 1410

    # Enterprises, Administration, and Participation (EAP)
    EAP_OIL_AND_GAS                                          = 3010
    EAP_PETROCHEMICAL_AND_RUBBER                             = 3020
    EAP_MINERAL_EXTRACTION                                   = 3030
    EAP_PULP_AND_PAPER                                       = 3040
    EAP_TEXTILE_AND_CLOTHING                                 = 3050
    EAP_METALLURGY_AND_STEELMAKING                           = 3060
    EAP_MACHINERY_EQUIPMENT_VEHICLE_AND_PARTS                = 3070
    EAP_PHARMACEUTICAL_AND_HYGIENE                           = 3080
    EAP_BEVERAGES_AND_TOBACCO                                = 3090
    EAP_PRINTERS_AND_PUBLISHERS                              = 3100
    EAP_CIVIL_CONSTRUCTION_BUILDING_AND_DECORATION_MATERIALS = 3110
    EAP_ELETRICITY                                           = 3120
    EAP_TELECOMMUNICATIONS                                   = 3130
    EAP_TRANSPORT_AND_LOGISTICS_SERVICES                     = 3140
    EAP_COMMUNICATION_AND_INFORMATION_TECHNOLOGY             = 3150
    EAP_SANITATION_WATER_AND_GAS_SERVICES                    = 3160
    EAP_MEDICAL_SERVICES                                     = 3170
    EAP_HOSTING_AND_TOURISM                                  = 3180
    EAP_WHOLESAIL_AND_RETAIL_COMMERCE                        = 3190
    EAP_FOREIGN_COMMERCE                                     = 3200
    EAP_AGRICULTURE                                          = 3210
    EAP_FOOD                                                 = 3220
    EAP_COOPERATIVES                                         = 3230
    EAP_BANKS                                                = 3240
    EAP_INSURANCE_AND_BROKERAGE_COMPANIES                    = 3250
    EAP_LEASING                                              = 3260
    EAP_PRIVATE_PENSION                                      = 3270
    EAP_FINANCIAL_INTERMEDIATION                             = 3280
    EAP_FACTORING                                            = 3290
    EAP_REAL_ESTATE_CREDIT                                   = 3300
    EAP_REFORESTATION                                        = 3310
    EAP_FISHING                                              = 3320
    EAP_PACKAGING                                            = 3330
    EAP_EDUCATION                                            = 3380
    EAP_SECURITIZATION_OF_RECEIVABLES                        = 3390
    EAP_TOYS_AND_RECREATIONAL                                = 3400
    EAP_STOCK_EXCHANGES                                      = 3410
    EAP_NO_CORE_BUSINESS                                     = 3990

    # Old descriptions.
    MISCELLANEOUS_SERVICES      = -1
    EAP                         = -2
    OTHER_INDUSTRIAL_ACTIVITIES = -3
    GENERAL_SERVICES            = -5

    def is_eap(self) -> bool:
        return self.value >= 3010 and self.value <= 3990

    def as_eap(self) -> Industry:
        if self.is_eap():
            return self
        
        return Industry(self.value + 2000)

    def as_non_eap(self) -> Industry:
        if self.is_eap():
            return Industry(self.value - 2000)

        return self