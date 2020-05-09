 # install.packages(c("dplyr", "fGarch", "ggplot2", "jsonlite", "magrittr", "NobBS", "sos", "curl", "ggpubr"))
library(jsonlite)
library(magrittr)
library(sos)
library(dplyr)
library(fGarch)
library(NobBS)
library(ggplot2)
library(ggpubr)
source("DataAggregation.R")
source("DistrictSimilarity.R")

generate_nobbs_estimates <- function(district_name, all_districts_data) {
  single_district_data <- all_districts_data[(district == district_name), ]
  if(nrow(single_district_data) <= 30) {
    print(paste(district_name, " has less than 30 cases"))
    return(NULL)
  }
  print(district_name)
  single_district_dates_alone <- single_district_data %>% select(onset_date, report_date)
  names(single_district_dates_alone ) <- c("onset_week", "report_week")
  nowcast_results <- NobBS(data=single_district_dates_alone, now=as.Date("2020-05-10"), units="1 day", 
                           onset_date="onset_week", report_date="report_week")
  print(nowcast_results$estimates)
  nowcasts <- nowcast_results$estimates
  nowcast_plot <- ggplot(nowcasts) + geom_line(aes(onset_date,estimate,col="Nowcast estimate"),linetype="longdash") +
    geom_line(aes(onset_date,n.reported,col="Reported to date"),linetype="solid") +
    scale_colour_manual(name="",values=c("indianred3","black"))+
    theme_classic()+
    geom_ribbon(fill="indianred3",aes(x = onset_date,ymin=nowcasts$lower, 
                                      ymax=nowcasts$upper),alpha=0.3)+
    xlab("Case onset date") + ylab("Estimated cases") +
    ggtitle(paste(district_name, " Nowcast"))
  
  nowcast_plot
}

# Get raw patient data
raw_patient_df <- consolidate_all_data()

# Get names of all districts with patients
district_wise_data <- fromJSON("https://api.covid19india.org/state_district_wise.json")
districts_list = list()
for(p in district_wise_data) { districts_list[names(p$districtData)] <- FALSE}
districts_list[["Unknown"]] <- NULL
districts_df = data.frame(names(districts_list))
colnames(districts_df) <- c("district")

# cleaning up patient data to remove tourist related data and retaining only the columns needed
patient_data = merge(x=districts_df, y=raw_patient_df, by.x='district', by.y='raw_data.detecteddistrict')

#### Calculation of onset date based on announcement date
num_patients <- nrow(patient_data)
# Using Skewed Gaussian with a mean of 9 days and standard deviation 4 to get the incubation time
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
all_districts_reliable_data <- all_districts_data[(all_districts_data$onset_date >= as.Date('2020-04-01')), ]
# Examples in all_districts_data dataframe
# district onset_date report_date
# Alappuzha	2020-01-18	2020-02-02
# Thrissur	2020-01-19	2020-01-30
# Kasaragod	2020-01-20	2020-02-03
# Agra	2020-02-17	2020-03-04
# East Delhi	2020-02-18	2020-03-02


# Get the plots for the top infected districts
district_grouped_data <- group_by(all_districts_reliable_data, district)
district_patient_counts <- summarise(district_grouped_data, n())
names(district_patient_counts) <- c("district", "count")
top_infected_districts <- top_n(district_patient_counts, 3, count)$district
plots_list <- lapply(top_infected_districts, generate_nobbs_estimates, all_districts_reliable_data)
ggarrange(plotlist = plots_list)

# Top Assam districts
assam_districts <- list("Cachar", "Bongaigaon", "Kamrup Metropolitan", "Goalpara", "Karimganj", "Kokrajhar")
plots_list <- lapply(assam_districts, generate_nobbs_estimates, all_districts_data)
ggarrange(plotlist = plots_list)

# Analysis on districts similar to that of Assam. 
assam_district <- "Karimganj"
similar_districts <- get_similar_districts_by_population(assam_district)
plots_list <- lapply(similar_districts, generate_nobbs_estimates, all_districts_data)
plots_list[sapply(plots_list, is.null)] <- NULL
ggarrange(plotlist = plots_list)
