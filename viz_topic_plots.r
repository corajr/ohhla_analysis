source("load_topics.r")

state <- load.mallet.state("lda/topic-state.gz")
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, "lda/metadata_all.csv")

numTopics <- length(tabulatedState$top.words)
all.topic.mis <- sapply(1:numTopics, function (x) { topic.mi(tabulatedState$state, x)})

mi.quantiles <- quantile(all.topic.mis)
middle.topics <- which(all.topic.mis > mi.quantiles[2] & all.topic.mis < mi.quantiles[4])

for (i in middle.topics) {
    name <- get.topic.name(tabulatedState, i)
    topic.plot(paste("plots", name, sep="/"), top.words.imi(tabulatedState, i))
}

# replicas <- replicate.states(tabulatedState)
# deviations <- deviation.from.replicas(tabulatedState, "year")
