require(ggplot2)

entropy <- function(p) {
    if (min(p) < 0 || sum(p) <= 0)
        return(NA)
    p.norm <- p[p>0]/sum(p)
    -sum(log2(p.norm)*p.norm)
}

# cribbed from benjamin schmidt with slight modification
# http://journalofdigitalhumanities.org/2-1/code-appendix-for-words-alone-by-benjamin-m-schmidt/

# Load a mallet file, keeping only the doc, word, and topic variables
load.mallet.state <- function(fileLocation = "topic-state.gz") {
  read.table(
    file=fileLocation,
    colClasses=c("integer","NULL","NULL","NULL","factor","integer"),
    comment.char="#",col.names=c("doc","NA","NA2","NA3","word","topic"))
}

get.topic.word.dists <- function(state) {
    m <- table(state$word, state$topic)
    scale(m, center=F, scale=colSums(m)) #normalize
}

replicate.states <- function(tabulatedState, n = 20) {
    topic.words <- tabulatedState$topic.words
    all.words <- rownames(topic.words)
    states <- list()
    state <- tabulatedState$state
    topic.positions <- list()

    for (topic in colnames(topic.words)) {
        topic.positions[[topic]] <- which(state$topic == topic)
    }

    for (i in 1:n) {
        new.state <- replicate.state(state, all.words, topic.words, topic.positions)
        states[[i]] <- new.state
    }
    states
}

augment.replicas <- function (replica.states, artistCsvFilename="artist.csv") {
    artists <- read.csv(artistCsvFilename)
    for (i in 1:length(replica.states)) {    
        replica.states[[i]] <- merge(replica.states[[i]], artists[, c("doc", "artist")], by="doc")
    }
    replica.states
}

replicate.state <- function(state, all.words, topic.words, topic.positions) {
    for (topic in colnames(topic.words)) {
        state[topic.positions[[topic]], "word"] <- sample(all.words, length(topic.positions[[topic]]), prob=topic.words[,topic], replace=TRUE)
    }
    state
}

get.replica.discrepancies <- function(tabulatedState, replicas, group="doc") {
    numTopics <- ncol(tabulatedState$doc.topics)
    mis <- NULL
    for (replica in replicas) {
        mis <- rbind(mis, sapply(1:numTopics, function (x) { topic.mi(replica, x, group)}))
    }
    mis
}

deviation.from.replicas <- function(tabulatedState, replica.mis, group="doc") {
    numTopics <- ncol(tabulatedState$doc.topics)
    deviations <- NULL
    for (topic in 1:numTopics) {
        all.mis.for.topic <- replica.mis[,topic]
        mi <- topic.mi(tabulatedState$state, topic, group)
        deviations <- c(deviations, (mi - mean(all.mis.for.topic)) / sd(all.mis.for.topic))
    }
    deviations
}

imi <- function(tabulatedState, topic, word) {
    state <- tabulatedState$state
    entropy(tabulatedState$doc.topics[,topic]) - entropy(table(state[state$word == word & state$topic == topic - 1,"doc"]))
}

imi.group <- function(tabulatedState, topic, word, group = "year") {
    state <- tabulatedState$state
    entropy(tabulatedState[[group]][,topic]) - entropy(table(state[state$word == word & state$topic == topic - 1, group]))
}

get.group.topics <- function(state, group = "year") {
    table(state[[group]], state$topic)
}

tabulate.state <- function(state) {
    tabulatedState <- list(state=state)
    tabulatedState$doc.topics <- get.group.topics(state, "doc")
    tabulatedState$topic.words <- get.topic.word.dists(state)
    numTopics <- ncol(tabulatedState$doc.topics)
    tabulatedState$top.words <- lapply(1:numTopics, function (x) { sort(tabulatedState$topic.words[,x], decreasing=T)[1:15] })
    tabulatedState
}

add.groups.to.state <- function(tabulatedState, metadataFilename = "metadata.csv") {
    metadata <- read.csv(metadataFilename)
    tabulatedState$state <- merge(tabulatedState$state, metadata, by="doc")
    # tabulatedState$state <- merge(tabulatedState$state, metadata[, c("doc", "year", "place", "typist", "artist")], by="doc")
    tabulatedState$year <- get.group.topics(tabulatedState$state, "year")
    tabulatedState$place <- get.group.topics(tabulatedState$state, "place")
    tabulatedState$artist <- get.group.topics(tabulatedState$state, "artist")
    tabulatedState
}

top.words.imi <- function(tabulatedState, topic, group="doc") {
    topic.results <- list()
    topic.words <- tabulatedState$top.words[[topic]]
    topic.results$words <- attr(topic.words, "names")
    topic.results$prob <- topic.words
    topic.results$imi <- sapply(topic.results$words , function (word) {
        imi(tabulatedState, topic, word)
    })
    topic.results
}

topic.mi <- function(state, topic, group="doc") {
    data <- state[state$topic==topic-1, c(group, "word")]
    n.k <- nrow(data)
    n.w.k <- table(data$word)
    n.d.k <- table(data[[group]])
    n.w.d.k <- table(data) # this is transposed; words are rows and docs are cols

    nonzeros <- which(n.w.d.k!=0, arr.ind=T)
    nwdk <- n.w.d.k[nonzeros]
    terms <- nwdk / n.k
    log.terms <- log((nwdk * n.k) / (n.w.k[nonzeros[,2]] * n.d.k[nonzeros[,1]]))
    sum(terms * log.terms)
}

topic.plot <- function (name, topic.obj) {
    df <- data.frame(imi=topic.obj$imi, prob=topic.obj$prob, words=topic.obj$words)
    filename <- paste(name, ".pdf", sep='')
    this.plot <- ggplot(df, aes(x=imi, y=1:length(prob), label=words)) +
        geom_point(aes(size=log(prob)), show_guide=FALSE) + scale_area(range=c(1,3)) +
        geom_text(size=4, hjust=-0.3) +
        theme_bw() +
        # ggtitle() +
        xlab("IMI(w,D|k)") +
        ylab("Rank") +
        scale_y_reverse()
    ggsave(filename, this.plot, width=4, height=3)
}

get.topic.name <- function(tabulatedState, i) {
    paste(attr(tabulatedState$top.words[[i]][1:3], "names"), collapse="_")
}

get.topic.labels <- function(tabulatedState) {
    doc.topics <- tabulatedState$doc.topics
    sapply(1:ncol(doc.topics), function (x) { get.topic.name(tabulatedState, x) })
}

# e.g.
# state <- load.mallet.state("lda/topic-state.gz")
# tabulatedState <- tabulate.state(state)
#
# all.topic.mis <- sapply(1:50, function (x) { topic.mi(state, x)})
#
# topic.obj <- top.words.imi(tabulatedState, 50) 
# topic.plot("topic50label", topic.obj)