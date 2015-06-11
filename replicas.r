source("load_topics.r")

state <- load.mallet.state("lda/topic-state.gz")
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, "lda/metadata_all.csv")

# replica.states <- replicate.states(tabulatedState, 100)
load("/Users/chrisjr/Dropbox/ldareplicas_all.gz")

replica.mis <- list()
# deviations <- list()
source("deviations")

groupings <- c("artist") #, "year", "place", "typist", "doc")
for (grouping in groupings) {
    replica.mis[[grouping]] <- get.replica.discrepancies(tabulatedState, replica.states, grouping)
    deviations[[grouping]] <- deviation.from.replicas(tabulatedState, replica.mis[[grouping]], grouping)
}

deviation.df <- stack(deviations)

deviance.plot <- ggplot(deviation.df, aes(x=reorder(ind, values, FUN=median), y=values)) + geom_boxplot() +
    ylab("Deviance") +
    xlab("Grouping") +
    theme_bw() +
    coord_flip()

ggsave("deviations.pdf", deviance.plot, width=4, height=3)