# News Feed Engine 🚀

Comprehensive AI-powered platform for content aggregation, analysis, and distribution across multiple social media platforms.

## Features

- **Content Aggregation**: Collect from 50+ news sources via RSS, APIs
- **AI Analysis**: Claude-powered content analysis and categorization
- **Video Generation**: Automated video creation with ElevenLabs + D-ID
- **Multi-Platform Publishing**: Publish to 9+ social networks simultaneously
- **Marketing Automation**: Campaign management and optimization
- **Real-time Analytics**: Trending detection and performance metrics
- **Enterprise Ready**: Kubernetes, Prometheus, Grafana, multi-tenancy support

## Quick Start

```bash
# Clone repository
git clone https://github.com/kushin77/news-feed-engine.git
cd news-feed-engine

# Start all services
docker-compose up -d

# Verify health
curl http://localhost:8080/health
```

## Architecture

- **news-feed-engine** (Go) - Core microservice
- **processor** (Python) - ML pipeline
- **social-media-platform** - Multi-platform integrations
- **marketing-engine** - Campaign automation
- **frontend** - React UI + Landing pages

## Documentation

- [Development Guide](docs/DEVELOPMENT.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security Framework](docs/SECURITY.md)

## License

MIT License - see LICENSE file

## Support

For issues, questions, or contributions, please open an issue or pull request.

---

**Migrated from**: https://github.com/elevatediq/main  
**Migration Date**: $(date)  
**Repository**: https://github.com/kushin77/news-feed-engine
