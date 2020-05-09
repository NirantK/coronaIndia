library(readxl)

get_all_district_population <- function() {
  census_data <- read_excel('IndiaCensus.xlsx')
  district_populations <- census_data[(census_data$Level == 'DISTRICT' & census_data$TRU =='Total'), ] %>%
    select(Name, TOT_P)
  district_populations
}

get_similar_districts_by_population <- function(choosen_district) {
  district_populations = get_all_district_population()
  actual_dist_pop = district_populations[(district_populations$Name == choosen_district), "TOT_P"]
  actual_pop <- actual_dist_pop$TOT_P[1]
  lower_limit <- (actual_pop*90)/100
  upper_limit <- (actual_pop*100)/100
  similar_districts <- district_populations[(district_populations$TOT_P >= lower_limit & 
                                              district_populations$TOT_P <= upper_limit), "Name"]
  similar_districts$Name
}
