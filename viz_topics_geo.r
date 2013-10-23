source("load_topics.r")
# source("deviations")
source("viz_plot_place.r")

state <- load.mallet.state("dmr/dmr.state.gz")
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, "dmr/metadata.csv")

topic.labels <- get.topic.labels(tabulatedState)

# topics.place.varying <- (sort(deviations$place, index.return=T, decreasing=T)$ix)[1:5]

state <- tabulatedState$state

topics.place.varying <- c(6,7)

topic.places <- list()
for (topic in topics.place.varying) {
    label <- topic.labels[topic]
    data <- state[state$topic==topic-1, c("lon", "lat")]
    topic.places[[label]] <- aggregate(data$lon, by=data, length)
}

for (label in names(topic.places)) {
    density_map(label, topic.places[[label]])
}