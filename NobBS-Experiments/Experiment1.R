library(jsonlite)
library(magrittr)
library(sos)
library(dplyr)
library(fGarch)
library(NobBS)

# Get raw patient data
raw_patient_df <- data.frame(fromJSON("https://api.covid19india.org/raw_data.json"))

# Get names of all districts with patients
district_wise_data <- fromJSON("https://api.covid19india.org/state_district_wise.json")
districts_list = list()
for(p in district_wise_data) { districts_list[names(p$districtData)] <- FALSE}
districts_list[["Unknown"]] <- NULL
districts_df = data.frame(names(districts_list))
colnames(districts_df) <- c("district")

# cleaning up patient data to remove tourist related data and retaining only the columns needed
patient_clean_df = merge(x=districts_df, y=raw_patient_df, by.x='district', by.y='raw_data.detecteddistrict')
patient_data <- patient_clean_df %>% select(district, raw_data.dateannounced)

#### Calculation of onset date based on announcement date
num_patients <- nrow(patient_data)
# Using Skewed Gaussian with a mean of 14 days and standard deviation 1 to get the incubation time
mu = 9
incubation_times <- floor(rsnorm(num_patients, mean=mu, sd=4, xi=-3))
# removing negative values by adding mean to them 
incubation_times[incubation_times<0] <- incubation_times[incubation_times<0] + mu
# Using Uniform Random sample in the interval of [1-3] to get the testing time
testing_time <- floor(runif(num_patients, min=1, max=4))
delay <- incubation_times + testing_time
onset_date <- as.Date(patient_data$raw_data.dateannounced, format ="%d/%m/%Y") - delay

# Create dataframe for all districts
report_date <- as.Date(patient_data$raw_data.dateannounced, format="%d/%m/%Y")
district <- patient_data$district
all_districts_data <- data.frame(district, onset_date, report_date)
# Example output of all_districts_data
# district  onset_date  report_date
# Adilabad	2020-03-27	2020-04-10
# Adilabad	2020-03-27	2020-04-10
# Adilabad	2020-03-27	2020-04-10
# Adilabad	2020-04-04	2020-04-19









