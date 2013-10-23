source("load_topics.r")
require("topicmodels")

lda.state <- load.mallet.state("lda/topic-state.gz")
dmr.state <- load.mallet.state("dmr/dmr.state.gz")

lda.tabulated <- tabulate.state(lda.state)
dmr.tabulated <- tabulate.state(dmr.state)

lda.tw <- lda.tabulated$topic.words
dmr.tw <- dmr.tabulated$topic.words

lda.words <- rownames(lda.tw)
dmr.words <- rownames(dmr.tw)

lda.to.trim <- lda.words[!(lda.words %in% dmr.words)]
lda.tw <- lda.tw[!(rownames(lda.tw) %in% lda.to.trim),]

dmr.to.trim <- dmr.words[!(dmr.words %in% lda.words)]
dmr.tw <- dmr.tw[!(rownames(dmr.tw) %in% dmr.to.trim),]

d <- distHellinger(t(lda.tw), t(dmr.tw))
equivalents <- max.col(1-d)

lda.labels <- get.topic.labels(lda.tabulated)
dmr.labels <- get.topic.labels(dmr.tabulated)

# if topic 2 in lda, topic 18 in dmr:
# equivalents[2] == 18

differences <- c()
for (i in 1:length(equivalents)) {
    print(paste(i, lda.labels[i], equivalents[i], dmr.labels[equivalents[i]], sep=" "))
    # differences <- c(differences, d[i, equivalents[i]])
}

