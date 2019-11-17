# Logistic regression models for binary classification evaluating both target variables 

rm(list = ls())

library(usdm)
library(stargazer)
library(caret)

set.seed(1)

# Set specific features as control variables
control_df <- function(df,dummy){
  df$reissue<-as.factor(df$reissue)
  df$crossover<-as.factor(df$crossover)
  df$time<-as.factor(df$time)
  df$success<-as.factor(df$success)
  df$long<-as.factor(df$long)
  df$genre<-as.factor(df$genre)
  
  if (dummy==FALSE){
    df$key<-as.factor(df$key)
    df$mode<-as.factor(df$mode)
    df$time_signature<-as.factor(df$time_signature)
  }
  return(df)
}

# Remove features that are multicollinear 
build_df <- function(df,target_var,hit=list(),miss=list(),dummy){
  df<-unique(df)
  
  if (dummy>0){
    # Feature set contains metadata features 
    if (dummy==1){
      df<-df[c("reissue","success","genre","crossover","time","long","interval","align")]
      v<-vifstep(df[-c(match("interval",colnames(df)),match("align",colnames(df)))],4)
      df<-control_df(df,TRUE)
    # Feature set contains metadata and audio features 
    } else if (dummy==2) {
      df<-df[c("energy","liveness","tempo","speechiness","acousticness","instrumentalness",
               "time_signature","danceability","key","valence","mode","reissue","success",
               "genre","echo_typ","echo_genre_typ","echo_artist_typ","crossover","time","long","interval","align")]
      v<-vifstep(df[-c(match("interval",colnames(df)),match("align",colnames(df)))],4)
      df<-control_df(df,FALSE)
    }
    df_colnames<-colnames(exclude(df,v))
    df<-df[c(df_colnames,target_var)]
  }
  # Full feature set
  else{
    v<-vifstep(df[-c(match("interval",colnames(df)),match("align",colnames(df)),match("X0",colnames(df)))],4)
    df<-control_df(df,FALSE)
    df_colnames<-colnames(exclude(df,v))
    df<-df[c(df_colnames,target_var)]
  }
  
  # Relevel target variables as hits and flops     
  agr_hit=as.logical((df[target_var][,1]==-1))
  for (h in hit){
    agr_hit=agr_hit+as.logical((df[target_var][,1]==h))
  }
  
  agr_miss=as.logical((df[target_var][,1]==-1))
  for (m in miss){
    agr_miss=agr_miss+as.logical((df[target_var][,1]==m))
  }
  
  df[as.logical(agr_miss),][target_var][,1]=0
  df[as.logical(agr_hit),][target_var][,1]=1
  df<-df[as.logical((agr_miss+agr_hit)),]
  df[target_var][,1]<-as.factor(df[target_var][,1])
  return(df)
}

# Read in feature sets and build DataFrames
path_tm10="data/model0_data.tsv"
path_tm20="data/model1_data.tsv"
path_tm40="data/model2_data.tsv"
path_tm80="data/model3_data.tsv"

df_tm10=read.table(file=path_tm10,sep='\t',header=TRUE)
df_tm20=read.table(file=path_tm20,sep='\t',header=TRUE)
df_tm40=read.table(file=path_tm40,sep='\t',header=TRUE)
df_tm80=read.table(file=path_tm80,sep='\t',header=TRUE)

# Interval feature sets 
interval_hit=c(34,35,40,41)
interval_miss=0
df_tm10_interval<-build_df(df_tm10,"interval",interval_hit,interval_miss,0)
df_tm20_interval<-build_df(df_tm20,"interval",interval_hit,interval_miss,0)
df_tm40_interval<-build_df(df_tm40,"interval",interval_hit,interval_miss,0)
df_tm80_interval<-build_df(df_tm80,"interval",interval_hit,interval_miss,0)
df_dummy_full_interval<-build_df(df_tm10,"interval",interval_hit,interval_miss,1)
df_dummy_echo_interval<-build_df(df_tm10,"interval",interval_hit,interval_miss,2)

# Alignment feature sets, funk genre excluded because of complete imbalance
align_hit=c(10,30,11)
align_miss=c(4,5)
df_tm10_align<-build_df(df_tm10,"align",align_hit,align_miss,0)
df_tm10_align=df_tm10_align[!df_tm10_align$genre==10,]
df_tm20_align<-build_df(df_tm20,"align",align_hit,align_miss,0)
df_tm20_align=df_tm20_align[!df_tm20_align$genre==10,]
df_tm40_align<-build_df(df_tm40,"align",align_hit,align_miss,0)
df_tm40_align=df_tm40_align[!df_tm40_align$genre==10,]
df_tm80_align<-build_df(df_tm80,"align",align_hit,align_miss,0)
df_tm80_align=df_tm80_align[!df_tm80_align$genre==10,]
df_dummy_full_align<-build_df(df_tm10,"align",align_hit,align_miss,1)
df_dummy_full_align=df_dummy_full_align[!df_dummy_full_align$genre==10,]
df_dummy_echo_align<-build_df(df_tm10,"align",align_hit,align_miss,2)
df_dummy_echo_align=df_dummy_echo_align[!df_dummy_echo_align$genre==10,]

# Model interval target variable 
model_tm10_interval <- glm(interval~.,data=df_tm10_interval,family = "binomial")
model_tm20_interval <- glm(interval~.,data=df_tm20_interval,family = "binomial")
model_tm40_interval <- glm(interval~.,data=df_tm40_interval,family = "binomial")
model_tm80_interval <- glm(interval~.,data=df_tm80_interval,family = "binomial")
model_dummy_full_interval <- glm(interval~.,data=df_dummy_full_interval,family = "binomial")
model_dummy_echo_interval <- glm(interval~.,data=df_dummy_echo_interval,family = "binomial")

# Model alignment target variable 
model_tm10_align <- glm(align~.,data=df_tm10_align,family = "binomial")
model_tm20_align <- glm(align~.,data=df_tm20_align,family = "binomial")
model_tm40_align <- glm(align~.,data=df_tm40_align,family = "binomial")
model_tm80_align <- glm(align~.,data=df_tm80_align,family = "binomial")
model_dummy_full_align <- glm(align~.,data=df_dummy_full_align,family = "binomial")
model_dummy_echo_align <- glm(align~.,data=df_dummy_echo_align,family = "binomial")

# Ordering for output in Stargazer
order=c("^long1$",c("^success1$","^success2$","^success3$"),"^crossover1$","^reissue1$",c("^genre1$","^genre2$",
  "^genre3$","^genre4$","^genre5$","^genre6$","^genre7$","^genre8$","^genre9$","^genre10$","^genre11$","^genre12$"),
  c("^time2$","^time3$","^time4$","^time5$","^time6$","^time7$","^time8$","^time9$","^time10$","^time11$"),
  "^echo_typ$","^echo_genre_typ$","echo_artist_typ$","^tempo$","^energy$","^speechiness$","^acousticness$","^danceability$",
  "valence$","^instrumentalness$","^liveness$","key","^mode1$","^time_signature1$","^typ$","^genre_typ$","^artist_typ$")

stargazer(model_dummy_full_align,model_dummy_echo_align,model_tm10_align,model_tm20_align,model_tm40_align,model_tm80_align,
          align=TRUE,type="latex",out="align_logistic_appendix.tex",order=order,digits=3)
stargazer(model_dummy_full_interval,model_dummy_echo_interval,model_tm10_interval,model_tm20_interval,model_tm40_interval,model_tm80_interval,
          align=TRUE,type="latex",out="interval_logistic_appendix.tex",order=order,digits=3)
stargazer(model_tm20_interval,model_tm20_interval,model_tm20_interval,
          model_tm20_interval,model_tm20_interval,model_tm20_interval,
          align=TRUE,type="latex",out="lasso_filler_appendix.tex",order=order,digits=3)

# Find predicted class from model using cross validation with 10 folds
find_pred<-function(df,target_var,dummy){
  # Splice data 
  folds<-createFolds(df[target_var][,1], k = 10, list = TRUE, returnTrain = FALSE)
  cv<-matrix(NA, nrow=10, ncol=4)
  index=1
  
  
  for (i in folds){
    train_df<-df[-c(unlist(i)),]
    test_df<-df[c(unlist(i)),]
    if (dummy==0){
      controls<-c("reissue","crossover","time","success","long","genre","key","mode","time_signature")
    } else{
      controls<-c("reissue","crossover","time","success","long","genre")
    }
    
    # Relevel control variables
    for (con in controls){
      if (!isTRUE(all.equal(levels(factor(train_df[con][,1])),levels(factor(test_df[con][,1]))))){
        diff_indices=setdiff(levels(factor(test_df[con][,1])),levels(factor(train_df[con][,1])))
        for (ind in diff_indices){
          test_df=test_df[!test_df[con][,1]==ind,]
        }
      }
    }
    
    # Initial model
    model<-glm(paste0(target_var,"~."),data=train_df,family = "binomial")
    y_pred=predict(model,test_df,type="response")
    
    cutoffs <- seq(0.1,0.9,0.05)
    f1_scores=rep(-1,length(cutoffs))
    c_ind=1
    
    # Scan cutoffs for labelling songs as hits or flops based on their predicted probability of belonging to some class
    for (coff in cutoffs){
      y_pred_factor<-as.factor(as.numeric(y_pred>coff))
      y_test_factor<-as.factor(as.numeric(test_df[target_var][,1]))
      levels(y_pred_factor)<-c("0","1")
      levels(y_test_factor)<-c("0","1")
      conf_mat<-table(y_pred_factor,y_test_factor)
      acc=sum(diag(conf_mat))/sum(conf_mat)
      prec = conf_mat[2,2]/sum(conf_mat[,2])
      rec = conf_mat[2,2]/sum(conf_mat[2,])
      f1=2*prec*rec/(prec+rec)
      if (!is.nan(f1)){
        f1_scores[c_ind]=f1
      }
      c_ind=c_ind+1
    }
    
    # Use best cutoff as defined by F1 score (usually around 0.5)
    threshold=cutoffs[which.max(f1_scores)]
    y_pred_factor<-as.factor(as.numeric(y_pred>threshold))
    y_test_factor<-as.factor(as.numeric(test_df[target_var][,1]))
    levels(y_pred_factor)<-c("0","1")
    levels(y_test_factor)<-c("0","1")
    conf_mat<-table(y_pred_factor,y_test_factor)
    acc=sum(diag(conf_mat))/sum(conf_mat)
    prec = conf_mat[2,2]/sum(conf_mat[,2])
    rec = conf_mat[2,2]/sum(conf_mat[2,])
    f1=2*prec*rec/(prec+rec)
    cv[index,]=c(acc,prec,rec,f1)
    index=index+1
  }
  return(cv)
}

# Perform cross-validation over all of the model feature sets 
cv_tm10_interval<-find_pred(df_tm10_interval,"interval",0)
cv_tm20_interval<-find_pred(df_tm20_interval,"interval",0)
cv_tm40_interval<-find_pred(df_tm40_interval,"interval",0)
cv_tm80_interval<-find_pred(df_tm80_interval,"interval",0)
cv_dummy_full_interval<-find_pred(df_dummy_full_interval,"interval",1)
cv_dummy_echo_interval<-find_pred(df_dummy_echo_interval,"interval",0)

cv_tm10_align<-find_pred(df_tm10_align,"align",0)
cv_tm20_align<-find_pred(df_tm20_align,"align",0)
cv_tm40_align<-find_pred(df_tm40_align,"align",0)
cv_tm80_align<-find_pred(df_tm80_align,"align",0)
cv_dummy_full_align<-find_pred(df_dummy_full_align,"align",1)
cv_dummy_echo_align<-find_pred(df_dummy_echo_align,"align",0)

# Write average results to file 
cv_interval<-rbind(apply(cv_tm10_interval,2,mean),apply(cv_tm20_interval,2,mean),
          apply(cv_tm40_interval,2,mean),apply(cv_tm80_interval,2,mean),
          apply(cv_dummy_full_interval,2,mean),apply(cv_dummy_echo_interval,2,mean))

cv_align<-rbind(apply(cv_tm10_align,2,mean),apply(cv_tm20_align,2,mean),
                   apply(cv_tm40_align,2,mean),apply(cv_tm80_align,2,mean),
                   apply(cv_dummy_full_align,2,mean),apply(cv_dummy_echo_align,2,mean))

rownames(cv_interval)=c("tm10","tm20","tm40","tm80","dummy","echo")
colnames(cv_interval)=c("accuracy","precision","recall","F1")
rownames(cv_align)=c("tm10","tm20","tm40","tm80","dummy","echo")
colnames(cv_align)=c("accuracy","precision","recall","F1")

write.table(cv_interval,"10fold_cv_binary_interval.tsv",sep="\t",col.names=TRUE,row.names=TRUE)
write.table(cv_align,"10fold_cv_binary_align.tsv",sep="\t",col.names=TRUE,row.names=TRUE)


