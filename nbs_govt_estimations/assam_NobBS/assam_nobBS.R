install.packages("ggplot2")
install.packages("NobBS")

library(NobBS)
library(ggplot2)


# function to predict reported cases for various deistice of Assam
# Input: csv file name for respective district( created using jupyter notebook)
# Output: write the estimated dataset as csv file

pred_covid_rep_cases <- function(file_name)
{
  print(file_name)
  district_df <- read.csv(file_name, stringsAsFactors = FALSE)
  district_df$onset_week <- as.Date(district_df$onset_week , format = "%Y-%m-%d")
  district_df$report_week <- as.Date(district_df$report_week , format = "%Y-%m-%d")
  district_df <- NobBS(data=district_df, now=as.Date("2020-04-24"),
                       units="1 day",onset_date="onset_week",report_date="report_week")
  print(file_name)
  write.csv(district_df$estimates,file_name, row.names = FALSE)
  # print(tail(district_df$estimates))
}

#set the working directory from which the files will be read from
curr_wor_dir = setwd("C:/Users/goswa/Downloads/NobBS-master/NobBS-master")

#create a list of the files from your target directory
file_list <- list.files(curr_wor_dir,pattern = "\\.csv$")

# Calling pred_covid_rep_cases for all the districts in Assam
for (i in 1:length(file_list)){
  pred_covid_rep_cases(file_list[i])
}
