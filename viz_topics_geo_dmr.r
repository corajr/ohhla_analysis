source("load_topics.r")
# source("deviations")
source("viz_plot_place.r")

state <- load.mallet.state("dmr/dmr.state.gz")
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, "dmr/metadata.csv")

topic.labels <- get.topic.labels(tabulatedState)

# topics.place.varying <- (sort(deviations$place, index.return=T, decreasing=T)$ix)[1:5]

state <- tabulatedState$state

topics.place.varying <- 1:length(topic.labels)
topic.places <- list()

place.topic.table <- table(state[, c("place","topic")])
place.means <- apply(place.topic.table, 1, mean)
place.sds <- apply(place.topic.table, 1, sd)

place.lon.lat <- unique(state[,c("place", "lon", "lat")])

for (topic in topics.place.varying) {
    label <- topic.labels[topic]
    data <- state[state$topic==topic-1, c("place")]
    unscaled <- table(data)
    df <- merge(data.frame(place=names(unscaled), value=as.numeric(unscaled)), place.lon.lat, by=c("place"),incomparables = NA)
    topic.places[[label]] <- df[,c("lon", "lat", "value")]
    # scaled <- (unscaled-place.means)/place.sds
    # df <- merge(data.frame(place=names(scaled), value=as.numeric(scaled)), place.lon.lat, by=c("place"),incomparables = NA)
    # devs <- df[,c("lon", "lat", "value")]
    # devs[,3] <- devs[,3]-min(devs[,3])
    # devs[,3] <- round(100*(devs[,3]/max(devs[,3])))
}

for (label in names(topic.places)) {
    density_map(topic.places[[label]], paste("../../dmr_densities", label, sep="/"))
}