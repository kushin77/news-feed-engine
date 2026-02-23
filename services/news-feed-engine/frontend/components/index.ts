// Main exports for @elevatediq/news-feed-frontend package

export {
  NewsFeedProvider,
  NewsFeed,
  ContentCard,
  VideoSummaryCard,
  NewsFeedSearch,
  CategoryFilter,
} from './NewsFeed';

export type {
  Creator,
  ContentItem,
  VideoSummary,
  NewsFeedConfig,
} from './NewsFeed';

export {
  EmbeddableNewsFeed,
  initEmbedWidget,
} from './EmbeddableWidget';
