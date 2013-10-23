source("load_topics.r")

state <- load.mallet.state("lda/topic-state.gz")
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, "lda/metadata_all.csv")

topic.labels <- get.topic.labels(tabulatedState)

word.over.time <- function (factored.state, topic, word) {
    word.years <- table(factored.state[factored.state$topic == topic - 1 & factored.state$word == word, "year"])
    all.words.years <- table(factored.state[, "year"])
    vals <- word.years/all.words.years
    data.frame(year=as.numeric(rownames(vals)), value=as.numeric(vals))
}

plot.words.over.time <- function(tabulatedState, topic) {
    factored.state <- tabulatedState$state
    factored.state$year <- factor(factored.state$year)

    top.words <- names(tabulatedState$top.words[[topic]])[1:3]
    for (word in top.words) {
        df <- word.over.time(factored.state, topic, word)
        filename <- paste("plots_over_time/", word, ".pdf", sep='')
        this.plot <- ggplot(df, aes(x=year, y=value)) +
            geom_line() +
            ggtitle(word) +
            xlab("Year") +
            ylab("Score") +
            ylim(0, 0.0027)
        ggsave(filename, this.plot, width=8, height=3)
    }
}

plot.words.over.time(tabulatedState, 40)