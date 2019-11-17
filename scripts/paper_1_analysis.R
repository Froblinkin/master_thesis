# Ordered logit modelling for data with The Echo Nest and metadata features

rm(list = ls())
require(stargazer)
require(ggplot2)
require(MASS)
require(reshape2)
require(grid)
require(gridExtra)
set.seed(1)

# Read in records and inverse peak position
path="data/logit_data_sp_echo.tsv"
df<-read.table(file=path,sep='\t',header=TRUE)
df$peak<-101-df$peak

# Set specific variables as controls (metadata features)
dummy<-names(df)[c(7,9,11:14,16:35)]
df1<-df
for (i in names(df)){
  if (i%in%dummy){
    df[,i]<-as.factor(df[,i])
  }
}
df$peak<-ordered(df$peak)

# Model (3) from Askin & Mauskapf's paper, typicality 
f1<-as.formula(paste(names(df)[16],'~',paste(names(df)[15],'+'),paste(names(df)[c(1:14,18:33)],collapse='+')))
m1<-polr(f1,method=c("logistic"), data=df, Hess=TRUE)
m1.coef<-data.frame(coef(summary(m1)))
m1.coef$pval=round((pnorm(abs(m1.coef$t.value),lower.tail=FALSE)*2),2)
m1.or=exp(coef(m1))

# Model (4) from Askin & Mauskapf's paper, typicality^2 
f2<-as.formula(paste(names(df)[16],'~',paste('I(',names(df)[15],'^2) +'),paste(names(df)[15],'+'),paste(names(df)[c(1:14,18:33)],collapse='+')))
m2<-polr(f2,method=c("logistic"), data=df, Hess=TRUE)
m2.coef<-data.frame(coef(summary(m2)))
m2.coef$pval=round((pnorm(abs(m2.coef$t.value),lower.tail=FALSE)*2),2)
m2.or=exp(coef(m2))

# Plot marginal probabilities for model (4)
# Probability of all songs peaking at positions 61-100
dat<-predict(m2,type='probs')
newdat<-cbind(df1$typ,rowSums(dat[,1:40]))
newdat<-as.data.frame(newdat)
colnames(newdat)<-c('typ','61to100')
lnewdat<-melt(newdat,id.vars='typ')
d1<-ggplot(lnewdat,aes(x=typ,y=value,colour=variable))+geom_point(color="#F8766D",alpha=0.1)+ theme(legend.position="none")
d1<-d1+stat_smooth(method="lm", se=TRUE, fill=NA,formula=y ~ poly(x, 2, raw=TRUE),colour="black")+theme_classic()
d1<-d1+xlab("")+ylab("") 

# Probability of all songs peaking at positions 41-60
dat<-predict(m2,type='probs')
newdat<-cbind(df1$typ,rowSums(dat[,41:60]))
newdat<-as.data.frame(newdat)
colnames(newdat)<-c('typ','41to60')
lnewdat<-melt(newdat,id.vars='typ')
d2<-ggplot(lnewdat,aes(x=typ,y=value,colour=variable))+geom_point(color="#C49A00",alpha=0.1)+ theme(legend.position="none")
d2<-d2+stat_smooth(method="lm", se=TRUE, fill=NA,formula=y ~ poly(x, 2, raw=TRUE),colour="black")+theme_classic()
d2<-d2+xlab("")+ylab("") 

# Probability of all songs peaking at positions 21-40
dat<-predict(m2,type='probs')
newdat<-cbind(df1$typ,rowSums(dat[,61:80]))
newdat<-as.data.frame(newdat)
colnames(newdat)<-c('typ','21to40')
lnewdat<-melt(newdat,id.vars='typ')
d3<-ggplot(lnewdat,aes(x=typ,y=value,colour=variable))+geom_point(color="#53B400",alpha=0.1)+ theme(legend.position="none")
d3<-d3+stat_smooth(method="lm", se=TRUE, fill=NA,formula=y ~ poly(x, 2, raw=TRUE),colour="black")+theme_classic()
d3<-d3+xlab("")+ylab("") 

# Probability of all songs peaking at positions 11-20
dat<-predict(m2,type='probs')
newdat<-cbind(df1$typ,rowSums(dat[,81:90]))
newdat<-as.data.frame(newdat)
colnames(newdat)<-c('typ','11to20')
lnewdat<-melt(newdat,id.vars='typ')
d4<-ggplot(lnewdat,aes(x=typ,y=value,colour=variable))+geom_point(color="#00C094",alpha=0.1)+ theme(legend.position="none")
d4<-d4+stat_smooth(method="lm", se=TRUE, fill=NA,formula=y ~ poly(x, 2, raw=TRUE),colour="black")+theme_classic()
dat<-predict(m2,type='probs')
d4<-d4+xlab("Probability of reaching rank")+ylab("") 

# Probability of all songs peaking at positions 6-10
newdat<-cbind(df1$typ,rowSums(dat[,91:95]))
newdat<-as.data.frame(newdat)
colnames(newdat)<-c('typ','6to10')
lnewdat<-melt(newdat,id.vars='typ')
d5<-ggplot(lnewdat,aes(x=typ,y=value,colour=variable))+geom_point(color="#00B6EB",alpha=0.1)+ theme(legend.position="none")
d5<-d5+stat_smooth(method="lm", se=TRUE, fill=NA,formula=y ~ poly(x, 2, raw=TRUE),colour="black")+theme_classic()
d5<-d5+xlab("")+ylab("") 

# Probability of all songs peaking at positions 2-5
dat<-predict(m2,type='probs')
newdat<-cbind(df1$typ,rowSums(dat[,96:99]))
newdat<-as.data.frame(newdat)
colnames(newdat)<-c('typ','2to5')
lnewdat<-melt(newdat,id.vars='typ')
d6<-ggplot(lnewdat,aes(x=typ,y=value,colour=variable))+geom_point(color="#A58AFF",alpha=0.1)+ theme(legend.position="none")
d6<-d6+stat_smooth(method="lm", se=TRUE, fill=NA,formula=y ~ poly(x, 2, raw=TRUE),colour="black")+theme_classic()
d6<-d6+xlab("")+ylab("") 

# Probability of all songs peaking at position 1
dat<-predict(m2,type='probs')
newdat<-cbind(df1$typ,dat[,100])
newdat<-as.data.frame(newdat)
colnames(newdat)<-c('typ','1')
lnewdat<-melt(newdat,id.vars='typ')
d7<-ggplot(lnewdat,aes(x=typ,y=value,colour=variable))+geom_point(color="#FB61D7",alpha=0.1)+ theme(legend.position="none")
d7<-d7+stat_smooth(method="lm", se=TRUE, fill=NA,formula=y ~ poly(x, 2, raw=TRUE),colour="black")+theme_classic()
d7<-d7+xlab("Typicality")+ylab("") 

# Legend for all plots
g_legend<-function(a.gplot){
  tmp <- ggplot_gtable(ggplot_build(a.gplot))
  leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box")
  legend <- tmp$grobs[[leg]]
  legend
}
legend <- g_legend(d)

# Combine all plots 
lay <- rbind(c(2,2,2,2,2,NA,1,1,1,1,1),
             c(3,3,3,3,3,NA,4,4,4,4,4),
             c(5,5,5,5,5,NA,6,6,6,6,6),
             c(7,7,7,7,7,NA,8,8,8,8,8))
grid.arrange(legend,d1,d2,d3,d4,d5,d6,d7, layout_matrix = lay)

#################################################################################################

# Read in similar data using Spotify genre definitions
path="thesis/data/paper_1b.tsv"
df<-read.table(file=path,sep='\t',header=TRUE)
df$peak<-101-df$peak
df2<-df

# Control variables
dummy<-names(df)[c(7,9,11:14,16:35)]
for (i in names(df)){
  if (i%in%dummy){
    df[,i]<-as.factor(df[,i])
  }
}
df$peak<-ordered(df$peak)

# Fit models (3) and (4)
f1<-as.formula(paste(names(df)[16],'~',paste(names(df)[15],'+'),paste(names(df)[c(1:14,18:19)],collapse='+'),paste0("+"),
                     paste(names(df)[c(21:32)],collapse='+'),collapse="+"))
m3<-polr(f1,method=c("logistic"), data=df, Hess=TRUE)

f2<-as.formula(paste(names(df)[16],'~',paste('I(',names(df)[15],'^2) +'),paste(names(df)[15],'+'),
                     paste(names(df)[c(1:14,18:19)],collapse="+"),paste0("+"),paste(names(df)[c(21:32)],collapse='+'),collapse="+"))
m4<-polr(f2,method=c("logistic"), data=df, Hess=TRUE)

# Write to file
order=c("^I(typ2)$","^typ$","^long1$","^success1$","^success2$","^success3$","^crossover1$","^reissue1$","^tempo$","^energy$","^speechiness$","^acousticness$","^mode1$","^danceability$","^valence$","^instrumentalness$","^liveness$","^key1$","^key2$","^key3$","^key4$","^key5$","^key6$","^key7$","^key8$","^key9$","^key10$","^key11$","^time_signature1$","^decade1$","^decade2$","^decade3$","^decade4$","^decade5$","^decade6$","^decade7$","^decade8$","^decade9$","^decade10$","^Blues1$","^Child1$","^Classical1$","^Electronic1$","^Folk..World....Country1$","^Funk...Soul1$","^Hip.Hop1$","^Jazz1$","^Latin1$","^Non.Music1$","^Pop1$","^Reggae1$","^Rock1$","^Stage...Screen1$","^blues1$","^country1$","^disco1$","^folk1$","^funk1$","^metal1$","^none1$","^pop1$","^rap1$","^r.b1$","^rock1$","^soul1$")
stargazer(m1,m2,m3,m4,type="text",out="critique_1.tex",digits=3,order=order)


# Show typicality histogram for both genre definitions
a<-hist(df1$typ,breaks=100,col=rgb(1,0,0,0.5),xlab="Typicality",ylab="Count",main="")
a<-hist(df2$typ,breaks=a$breaks,col=rgb(0,0,1,0.5),add=TRUE,legend=TRUE)
legend(inset=0.1,"topleft", legend=c("Discogs","Spotify"), col=c(rgb(1,0,0,0.5),  rgb(0,0,1,0.5)), pt.cex=2, pch=15 )

#################################################################################################

# Revert peak position to original value
df$peak<-101-as.numeric(df$peak)

# row_slice
#
# Returns thes number of songs with some typicality value below a threshold. 
# @param df song record DataFrame
# @param thresh threshold for typicality values 
row_slice<-function(df,thresh){
  c(length(df[which((df[df$typ<thresh,]$peak==1)),]$peak),
  length(df[which((df[df$typ<thresh,]$peak>1)&(df[df$typ<thresh,]$peak<=5)),]$peak),
  length(df[which((df[df$typ<thresh,]$peak>5)&(df[df$typ<thresh,]$peak<=10)),]$peak),
  length(df[which((df[df$typ<thresh,]$peak>10)&(df[df$typ<thresh,]$peak<=20)),]$peak),
  length(df[which((df[df$typ<thresh,]$peak>20)&(df[df$typ<thresh,]$peak<=40)),]$peak),
  length(df[which((df[df$typ<thresh,]$peak>40)&(df[df$typ<thresh,]$peak<=60)),]$peak),
  length(df[which((df[df$typ<thresh,]$peak>60)&(df[df$typ<thresh,]$peak<=100)),]$peak))
}

# Find song counts for different typicality thresholds
peak_size<-data.frame(typ_range=c('0.0<=typ<0.7','0.7<=typ<0.75','0.75<=typ<0.8','0.8<=typ<0.85','0.85<=typ<0.9','typ>0.9'),
  rbind(row_slice(df,0.7),
      row_slice(df,0.75)-row_slice(df,0.7),
      row_slice(df,0.8)-row_slice(df,0.75),
      row_slice(df,0.85)-row_slice(df,0.8),
      row_slice(df,0.9)-row_slice(df,0.85),
      row_slice(df,0.95)-row_slice(df,0.9)
))
colnames(peak_size)<-c('typ_range','1','2-5','6-10','11-20','21-40','41-60','61-100')
melt_peak<-melt(peak_size,id='typ_range')

# Plot counts
p<-ggplot(melt_peak,aes(x=typ_range,y=variable))+geom_point(aes(size=value),color='blue')+theme_classic()
p<-p+xlab("Typicality range")+ylab("Peak position")
p$labels$size<-"Count"

# Find normalized song counts for thresholds
peak_size<-data.frame(typ_range=c('0.0<=typ<0.7','0.7<=typ<0.75','0.75<=typ<0.8','0.8<=typ<0.85','0.85<=typ<0.9','typ>0.9'),
                      rbind(row_slice(df,0.7)/sum(row_slice(df,0.7)),
                            (row_slice(df,0.75)-row_slice(df,0.7))/sum(row_slice(df,0.75)-row_slice(df,0.7)),
                            (row_slice(df,0.8)-row_slice(df,0.75))/sum(row_slice(df,0.8)-row_slice(df,0.75)),
                            (row_slice(df,0.85)-row_slice(df,0.8))/sum(row_slice(df,0.85)-row_slice(df,0.8)),
                            (row_slice(df,0.9)-row_slice(df,0.85))/sum(row_slice(df,0.9)-row_slice(df,0.85)),
                            (row_slice(df,0.95)-row_slice(df,0.9))/sum(row_slice(df,0.95)-row_slice(df,0.9))
                            #(row_slice(df,1)-row_slice(df,0.95))/sum(row_slice(df,1)-row_slice(df,0.95))
))
colnames(peak_size)<-c('typ_range','1','2-5','6-10','11-20','21-40','41-60','61-100')
melt_peak<-melt(peak_size,id='typ_range')

# Plot normalized counts
p<-ggplot(melt_peak,aes(x=typ_range,y=variable))+geom_point(aes(size=value),color='blue')+theme_classic()
p<-p+xlab("Typicality range")+ylab("Peak position")
p$labels$size<-"Normalized count"