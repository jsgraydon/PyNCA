library(dplyr)
library(ggplot2)
library(readr)

time_seq <- c(0, 6, 12, 24, 48, 72, 96, 120, 144, 168)
dose_seq <- c(100, rep(0, 9))

hl <- 8  # Half life (t1/2) in hours
k <- log(2) / hl  # Elimination rate constant (k)
C0 <- 100  # Initial concentration
conc_trend <- round(C0 * exp(-k * time_seq), 2) # Concentration at each time point


df <- tibble(ID = rep(1:10, each = 10),
             TIME = rep(time_seq, times = 10), 
             trend = rep(conc_trend, times = 10), #rep(round(conc_trend * rnorm(10, mean = 4, sd = 2), 2), times = 10),
             DOSE = rep(dose_seq, times = 10)) |>
  rowwise() |>
  mutate(CONC = trend * runif(n = 1, min = 1, max = 3), .keep = "unused") |>
  ungroup() |>
  mutate(CONC = round(CONC, 2))

df_summ <- df |>
  summarize(across(CONC, list(mean, sd, median, min, max)), .by = TIME)

ggplot(data = df, aes(x = TIME, y = CONC, color = as.factor(ID))) +
  geom_point() +
  stat_summary(fun = median, geom = "line", color = "red", linewidth = 1) 

write_csv(x = df, file = "./test_data.csv")


