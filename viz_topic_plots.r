source("load_topics.r")


do.plots <- function(model.type, state.file, metadata.file) {
    state <- load.mallet.state(state.file)
    tabulatedState <- tabulate.state(state)
    tabulatedState <- add.groups.to.state(tabulatedState, metadata.file)

    numTopics <- length(tabulatedState$top.words)
    all.topic.mis <- sapply(1:numTopics, function (x) { topic.mi(tabulatedState$state, x)})

    mi.quantiles <- quantile(all.topic.mis)
    middle.topics <- which(all.topic.mis > mi.quantiles[2] & all.topic.mis < mi.quantiles[4])

    for (i in 1:numTopics) {
        name <- get.topic.name(tabulatedState, i)
        topic.plot(paste(paste("plots", model.type, sep="_"), name, sep="/"), top.words.imi(tabulatedState, i))
    }    
}
# do.plots("lda", "lda/topic.state.gz", "lda/metadata_all.csv")
do.plots("dmr", "dmr/dmr.state.gz", "dmr/metadata.csv")

# replicas <- replicate.states(tabulatedState)
# deviations <- deviation.from.replicas(tabulatedState, "year")
