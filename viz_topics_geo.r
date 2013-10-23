source("load_topics.r")
source("deviations")

state <- load.mallet.state("lda/topic-state.gz")
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, "lda/metadata_all.csv")

topic.labels <- get.topic.labels(tabulatedState)

topics.place.varying <- (sort(deviations$place, index.return=T, decreasing=T)$ix)[1:5]

state <- tabulatedState$state

topic.places <- list()
for (topic in topics.place.varying) {
    label <- topic.labels[topic]
    data <- state[state$topic==topic-1, c("lon", "lat")]
    topic.places[[label]] <- aggregate(data$lon, by=data, length)
}

write.csv("check.word.crew.csv")