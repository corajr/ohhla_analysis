source("load_topics.r")
require("rjson")

state.file <- "lda/topic-state.gz"
metadata.file <- "lda/metadata.csv"

state <- load.mallet.state(state.file)
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, metadata.file)

numTopics <- length(tabulatedState$top.words)
all.topic.mis <- sapply(1:numTopics, function (x) { topic.mi(tabulatedState$state, x)})

# mi.quantiles <- quantile(all.topic.mis)
# middle.topics <- which(all.topic.mis > mi.quantiles[2] & all.topic.mis < mi.quantiles[4])

imis <- list()
for (i in 1:numTopics) {
    imis[[i]] <- top.words.imi(tabulatedState, i)
}

imi.string <- toJSON(imis)
write(imi.string, file="imis.txt")
#    topic.plot(paste(paste("plots", model.type, sep="_"), name, sep="/"), top.words.imi(tabulatedState, i))
    # name <- get.topic.name(tabulatedState, i)
#    topic.plot(paste(paste("plots", model.type, sep="_"), name, sep="/"), top.words.imi(tabulatedState, i))
# }