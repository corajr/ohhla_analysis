source("load_topics.r")

state <- load.mallet.state("lda/topic-state.gz")
tabulatedState <- tabulateState(state)

numTopics <- length(tabulatedState$top.words)
all.topic.mis <- sapply(1:numTopics, function (x) { topic.mi(tabulatedState$state, x)})

mi.quantiles <- quantile(all.topic.mis)
middle.topics <- which(all.topic.mis > mi.quantiles[2] & all.topic.mis < mi.quantiles[4])

for (i in middle.topics) {
    name <- paste(rownames(tabulatedState$top.words[[i]][1:3]), collapse="_")
    topic.plot(name, top.words.imi(tabulatedState, i))
}