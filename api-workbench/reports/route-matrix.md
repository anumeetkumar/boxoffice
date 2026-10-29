# API route and request comparison

Static declarations from both APKs. A shared path does not establish shared IDs, media inventory, credentials, authorization or response semantics. Required fields hidden behind FieldMap/Body remain subject to call-site or runtime evidence.

| Verb | Route | Providers | Movie method | DeepCine method |
| --- | --- | --- | --- | --- |
| GET | `/api/v2/site_report` | deepcine |  | setName |
| POST | `/api/ad/get_clipbrd` | deepcine |  | getClipBoard |
| POST | `/api/ad/get_list` | deepcine, movie | getAdInfo | getAdInfo |
| POST | `/api/barrage/add` | deepcine, movie | w | requestHomeVideoDetailAddBarrage |
| POST | `/api/barrage/get_list` | deepcine, movie | I | requestHomeVideoDetailBarrageList |
| POST | `/api/channel/get_info` | deepcine, movie | k | requestHomRecommendeMultipleVideoList |
| POST | `/api/channel/get_list` | deepcine, movie | d | getHomeTitleList |
| POST | `/api/data/action` | deepcine, movie | y | getStatisInfo |
| POST | `/api/discuss/add` | deepcine |  | requestHomeVideoDetailAddComment |
| POST | `/api/discuss/get_list_new` | deepcine, movie | B | requestHomeVideoDetailCommentList |
| POST | `/api/discuss/remove` | deepcine, movie | v | requestHomeVideoDetailDelComment |
| POST | `/api/eye/feed` | deepcine |  | requestTypeEyeList |
| POST | `/api/eye/feed_info` | deepcine |  | getVideoDetailList |
| POST | `/api/eye/feed_list` | deepcine |  | getCategoryDetailList |
| POST | `/api/eye/img_category` | deepcine |  | getCategoryList |
| POST | `/api/eye/search` | deepcine |  | requestTypeList |
| POST | `/api/eye/topic` | deepcine |  | getEyeRankList |
| POST | `/api/eye/user_history` | deepcine |  | getMaJiaUserHistroy |
| POST | `/api/invited/my_spread` | deepcine, movie | M | netCineFungetExtensionShareInfo |
| POST | `/api/invited/vod_share` | deepcine, movie | L | getVideoShare |
| POST | `/api/log/ad` | deepcine, movie | j | getAdStatisInfo |
| POST | `/api/order/add` | deepcine |  | getOrderInfo |
| POST | `/api/order/get_list` | deepcine, movie | N | getOrderList |
| POST | `/api/payment/get_list` | deepcine |  | getVipList |
| POST | `/api/playlet/back_popup` | deepcine |  | getShortRecommend |
| POST | `/api/playlet/channel_info` | deepcine |  | getShortChannelInfo |
| POST | `/api/playlet/channel_list` | deepcine |  | getShortHomeTitleList |
| POST | `/api/playlet/collect` | deepcine |  | setShortCollect |
| POST | `/api/playlet/index_recommend` | deepcine |  | indexRecommend |
| POST | `/api/playlet/info` | deepcine |  | setShortInfo |
| POST | `/api/playlet/info_recommend` | deepcine |  | getShortInfoRecommendList |
| POST | `/api/playlet/like` | deepcine |  | setShortLike |
| POST | `/api/playlet/report_start_play` | deepcine |  | reportStartPlay |
| POST | `/api/playlet/result` | deepcine |  | getShortSearchList |
| POST | `/api/playlet/screen` | deepcine |  | getShortFilterList |
| POST | `/api/playlet/suggest` | deepcine |  | getShortSearchExtendWord |
| POST | `/api/playlet/topic_list` | deepcine |  | getShortTopicList |
| POST | `/api/playlet/topic_video_list` | deepcine |  | getShortTopicInfoList |
| POST | `/api/playlet/type` | deepcine |  | getShortFilterTypeList |
| POST | `/api/public/feedback` | deepcine, movie | t | getnetCineFunFeedBackSubmit |
| POST | `/api/public/get_sys_conf` | deepcine, movie | O, R, h | getPublicSysConf, getPublicSysConfAd, getPublicSysConfShortVideo |
| POST | `/api/public/init` | deepcine, movie | G | netCineFungetInitUserDevice |
| POST | `/api/public/login` | deepcine, movie | s | getLoginUserSubmit |
| POST | `/api/public/register` | deepcine, movie | A | getRegieterUserAndAutoLogin |
| POST | `/api/public/report_ad_info` | deepcine |  | setAdinfo |
| POST | `/api/public/upload_file` | deepcine, movie | z | getUploadFile |
| POST | `/api/search/hot_search` | deepcine, movie | F | getNewHotSearchVideoList |
| POST | `/api/search/recommend` | deepcine, movie | r | requestHomRecommendeMultipleGussLikeList |
| POST | `/api/search/result` | deepcine, movie | l | getSearchList |
| POST | `/api/search/screen` | deepcine, movie | C, m | getGuessVideoList, getSearchVideoList |
| POST | `/api/search/suggest` | deepcine, movie | o | getSearchExtendWord |
| POST | `/api/short_play/list` | movie | D |  |
| POST | `/api/topic/change` | deepcine, movie | x | requestHomeModuleChangeVideoList |
| POST | `/api/topic/like_list` | deepcine |  | getSimilarVideoList |
| POST | `/api/topic/list` | deepcine, movie | g | getSpecialNewList, getTopicNewList |
| POST | `/api/topic/vod_list` | deepcine, movie | K, a, p | getRankList, getSpecialDetailNewList, requestHomeModuleMoreVideoList |
| POST | `/api/type/get_list` | deepcine, movie | n | getChannelFilter |
| POST | `/api/user/active_vip` | deepcine |  | netCineFungetActiveVip |
| POST | `/api/user/down` | deepcine, movie | P | netCineFungetDownloadStatisInfo |
| POST | `/api/user/feedback_list` | deepcine, movie | Q | getFeedBackRecord |
| POST | `/api/user/get_activity` | deepcine |  | getLookVideoFree |
| POST | `/api/user/info` | deepcine, movie | c | getMineUserInfo |
| POST | `/api/user/my_invited` | deepcine, movie | q | getExtensionShareRecord |
| POST | `/api/user/update` | deepcine, movie | S | getMinenetCineFunEditUserInfo |
| POST | `/api/user_history/add` | deepcine, movie | u | requestHomeVideoDetailStayTime |
| POST | `/api/user_vod/add` | deepcine, movie | f | requestHomeVideoDetailCollection |
| POST | `/api/user_vod/get_list` | deepcine, movie | E, J, e | getCollection, getCollectionSpecial, getMineCollectionSpecial, getVideoCollection |
| POST | `/api/user_vod/remove` | movie | H |  |
| POST | `/api/user_vod/remove_new` | deepcine |  | requestDelCollectionVideo |
| POST | `/api/user_vod/remove_topic` | deepcine |  | requestHomeVideoDetailDelCollection |
| POST | `/api/v1/shoply` | deepcine |  | getShortList |
| POST | `/api/vod/info` | deepcine |  | getHomeVideoDetailList |
| POST | `/api/vod/info_new` | deepcine, movie | b, i | getHomeVideoDetailListNew |
| POST | `/api/vod_info/urge_more` | deepcine |  | getUrgeMore |
| POST | `/api/vod_short/list` | deepcine |  | getSmallVideoList, getTKList |
| POST | `/api/vod_short/list_new` | deepcine |  | getNewSmallVideoList |
| POST | `/sunshine/user/cancelFavorite` | deepcine |  | requestHomeVideoDetailCancelCollection |
| POST | `/sunshine/user/getDefault9headImg` | deepcine |  | getHeadImageInfo |
| POST | `/sunshine/user/getFavoriteList` | deepcine |  | getMineCollectionList, getSpecialCollectionList |
| POST | `/sunshine/user/getShareInfo` | deepcine |  | getShareInfo |
| POST | `/sunshine/user/getSuggestTypes` | deepcine |  | getFeedBackType |
| POST | `/sunshine/user/getSuggetReplyState` | deepcine |  | getFeedbackReplay |
| POST | `/sunshine/user/insertSuggest` | deepcine, movie | T | requestHomeVideoDetailFeedback |
| POST | `/sunshine/user/login` | deepcine |  | getMineInfo |
| POST | `/sunshine/user/operModuleToFavorite` | deepcine |  | getSpecialDetailNewCollection |
| POST | `/sunshine/user/registerUser` | deepcine |  | getRegieterUserSubmit |
| POST | `/sunshine/user/updateDeviceToken` | deepcine |  | getDeviceToken |
| POST | `/sunshine/video/addCommentReport` | deepcine |  | requestHomeVideoDetailReportComment |
| POST | `/sunshine/video/addCopyCodeClickNum` | deepcine |  | getVideoCopyClickNum |
| POST | `/sunshine/video/addPlayError` | deepcine |  | requestHomeVideoDetailAddPlayError |
| POST | `/sunshine/video/getHomePageFilterCondition` | deepcine |  | requestHomeMultipleCategoryList |
| POST | `/sunshine/video/getHomePageVides` | deepcine |  | requestHomeMultipleVideoList |
| POST | `/sunshine/video/getHotSearch` | deepcine |  | getHotSearchVideoList |
| POST | `/sunshine/video/getPorjectVideosById` | deepcine |  | getSpecialDetail |
| POST | `/sunshine/video/getRankList` | deepcine |  | getRankType |
| POST | `/sunshine/video/getShortVideoList` | deepcine |  | getShortVideoList |
| POST | `/sunshine/video/getSimpleWordsFilter` | deepcine |  | requestHomeMultipleSpecialList |
| POST | `/sunshine/video/getSlideVideos` | deepcine, movie | V | getHomeVideoSlideList |
| POST | `/sunshine/video/getUploadVideoList` | deepcine |  | getMineUploadVideo |
| POST | `/sunshine/video/getVideoByCopyCode` | deepcine |  | netCineFungetVideoByCopyCode |
| POST | `/sunshine/video/newChangeBatch` | deepcine |  | requestHomeModuleChangeVideo |
| POST | `/sunshine/video/projectList` | deepcine |  | getSpecialList |
| POST | `/sunshine/video/showHomePageVideos` | deepcine |  | requestHomeVideoList |
| POST | `/sunshine/video/showHomePageVideosForPage` | deepcine, movie | U | getHomeVideoList |
