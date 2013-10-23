source("load_topics.r")
load("/Users/chrisjr/Dropbox/ldareplicas.gz")
replica.states <- augment.replicas(replica.states, "lda/artist.csv")
save("replica.states", compress="gzip", file="/Users/chrisjr/Dropbox/ldareplicas_all.gz")