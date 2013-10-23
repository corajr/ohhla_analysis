source("load_topics.r")

state <- load.mallet.state("dmr/dmr.state.gz")
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, "dmr/metadata.csv")

features <- read.csv("dmr_features.csv")
feature.labels <- read.csv("dmr_feature_labels.csv")

num.topics <- max(features$topic) + 1

topic.features <- list()
default.features <- c()

for (i in 1:num.topics) {
    data <- features[features$topic == i - 1, c("feature", "value")]
    default.feature.idx <- data$feature == "<default>"
    default.feature <- data[default.feature.idx,"value"]
    default.features[i] <- default.feature
    other.features <- data[!default.feature.idx,]
    other.features[,"value"] <- exp(default.feature + other.features[,"value"])
    top.features <- other.features[sort(other.features$value, decreasing=T, index.return=T)$ix,][1:5,]
    name <- get.topic.name(tabulatedState, i)
    topic.features[[name]] <- merge(top.features, feature.labels, by="feature", sort=F)
}

feature.get.topics <- function(feature) {
    label <- feature.labels[feature.labels$feature == feature, "label"]
    data <- features[features$feature == feature,]
    topic.values <- data.frame(topic=NULL, value=NULL)
    for (i in 1:num.topics) {
        default.feature <- default.features[i]
        topic.values <- rbind(topic.values, list(topic=i, value=exp(default.feature + data[data$topic==i-1,"value"])))
    }
    top.topics <- topic.values[sort(topic.values$value, decreasing=T, index.return=T)$ix,][1:10,]
    top.topics$topic <- sapply(top.topics$topic, function(topic) {get.topic.name(tabulatedState, topic-1)})
    top.topics
}

# artist8 = 2pac