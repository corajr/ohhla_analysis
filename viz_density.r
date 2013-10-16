require(spatstat)
require(RColorBrewer)
require(maps)
library(maptools)

# usdat <- data.frame(x=runif(50, -115, -85), y=runif(50, 33, 41), z=runif(50, 
# 0, 100))

# map('usa')
# points(usdat$x, usdat$y)  # do they fall in there?

usmap <- map('usa', fill=TRUE, col="transparent", plot=FALSE)
uspoly <- map2SpatialPolygons(usmap, IDs=usmap$names, 
proj4string=CRS("+proj=longlat +datum=wgs84"))
spatstat.options(checkpolygons=FALSE)
usowin <- as.owin.SpatialPolygons(uspoly)
spatstat.options(checkpolygons=TRUE)

# worldmap <- map('world', fill=TRUE, col="transparent", plot=FALSE)
# worldpoly <- map2SpatialPolygons(worldmap, IDs=worldmap$names, 
#     proj4string=CRS("+proj=longlat +datum=wgs84"))
# spatstat.options(checkpolygons=FALSE)
# worldowin <- as.owin.SpatialPolygons(worldpoly)
# spatstat.options(checkpolygons=TRUE)

density_map <- function (name) {
    pdf(file=paste(name, "_density.pdf", sep=''), height=4, width=5)
    datapts <- read.csv(paste(name, ".csv", sep=''))
    mapdat <- data.frame(x=datapts[,1], y=datapts[,2], z=datapts[,3])
    # Create a spatstat ppp object
    pts <- as.ppp(mapdat, W=usowin)
    # plot(pts)
    # Plot a a density surface
    # plot(density.ppp(pts))
    plot(density.ppp(pts, bw.diggle(pts), diggle=TRUE))
    dev.off()
}
density_map("allsongs")