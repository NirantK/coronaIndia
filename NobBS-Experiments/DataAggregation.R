# install.packages("tidyverse")
library(jsonlite)
library(tidyverse)

consolidate_all_data <- function( ) {
  patient_data_1 <- data.frame(fromJSON("https://api.covid19india.org/raw_data1.json"))
  patient_data_2 <- data.frame(fromJSON("https://api.covid19india.org/raw_data2.json"))
  
  all_patient_information <- patient_data_1 %>% select(raw_data.detecteddistrict, raw_data.dateannounced)
  all_patient_information <- rbind(all_patient_information, patient_data_2 %>% select(raw_data.detecteddistrict, 
                                                                                      raw_data.dateannounced))
  
  patient_data_3 <- data.frame(fromJSON("https://api.covid19india.org/raw_data3.json"))
  patient_data_3_with_district <- patient_data_3[(patient_data_3$raw_data.detecteddistrict != ""), ]
  patient_data_3_with_district$raw_data.numcases <- as.integer(patient_data_3_with_district$raw_data.numcases)
  patient_data_3_positive_cases <- patient_data_3_with_district[(patient_data_3_with_district$raw_data.numcases > 0), ]
  patient_data_3_positive_cases <- patient_data_3_positive_cases %>% select(raw_data.detecteddistrict, 
                                                                            raw_data.dateannounced, raw_data.numcases)
  
  bloated_districts <- rep(patient_data_3_positive_cases$raw_data.detecteddistrict, patient_data_3_positive_cases$raw_data.numcases)
  bloated_datedetected <- rep(patient_data_3_positive_cases$raw_data.dateannounced, patient_data_3_positive_cases$raw_data.numcases)
  patient_data_3_formatted <- data.frame(bloated_districts, bloated_datedetected)
  patient_data_3_formatted <- patient_data_3_formatted %>% rename(raw_data.detecteddistrict=bloated_districts, raw_data.dateannounced=bloated_datedetected)
  
  all_patient_information <- rbind(all_patient_information, patient_data_3_formatted)
  all_patient_information
}
