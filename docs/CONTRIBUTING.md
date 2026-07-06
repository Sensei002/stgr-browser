# Contributing to STGR Browser

Thank you for your interest in contributing to STGR Browser! This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and constructive. We follow the [Mozilla Community Participation Guidelines](https://www.mozilla.org/en-US/about/governance/policies/participation/).

## How to Contribute

### 1. Reporting Bugs

- **Check existing issues** first
- Use the bug report template
- Include:
  - STGR Browser version
  - Operating system
  - Steps to reproduce
  - Expected vs actual behavior
  - Screenshots if applicable
  - about:support information

### 2. Feature Requests

- Describe the problem you're solving
- Explain why STGR is the right place for this feature
- Consider performance impact
- Consider privacy implications
- Propose an implementation approach

### 3. Code Contributions

#### Getting Started

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/YOUR-USERNAME/stgr-browser.git
cd stgr-browser

# Set up development environment
./scripts/setup.sh

# Create a branch
git checkout -b feature/my-feature
```

#### Development Process

1. **Find an issue** to work on, or create one
2. **Discuss** your approach with the community
3. **Write code** following our coding standards
4. **Test** your changes
5. **Submit a pull request**

#### Pull Request Checklist

- [ ] Code follows STGR coding standards
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No telemetry or data collection added
- [ ] Performance impact considered
- [ ] Privacy impact considered
- [ ] License headers added
- [ ] Changelog updated

#### Code Review Process

1. PR is reviewed by at least one maintainer
2. Automated CI checks must pass
3. Performance regression tests pass
4. Privacy review (if applicable)
5. Merge after approval

### 4. Documentation

Documentation improvements are always welcome:

- Fix typos or broken links
- Add missing documentation
- Improve code comments
- Write tutorials
- Translate documentation

### 5. Testing

Help us improve test coverage:

- Write unit tests for STGR components
- Write integration tests
- Test on different platforms
- Performance testing
- Memory usage profiling

## Development Areas

### Priority Areas

- [ ] **Gaming Mode**: Improve game detection, add more optimizations
- [ ] **Memory Optimization**: Further reduce RAM usage
- [ ] **Startup Time**: Make startup even faster
- [ ] **UI/UX**: Refine the minimal interface
- [ ] **Vertical Tabs**: Implement optional vertical tab layout
- [ ] **Tab Groups**: Implement tab grouping
- [ ] **PDF Viewer**: Enhance the built-in PDF viewer
- [ ] **Reader Mode**: Improve reading experience
- [ ] **Downloads Manager**: Modernize the downloads UI
- [ ] **Screenshot Tool**: Enhance screenshot capabilities
- [ ] **QR Code Generator**: Implement QR code generation
- [ ] **Installers**: Improve installer for all platforms
- [ ] **Auto-Update**: Implement delta updates
- [ ] **Build System**: CI pipeline improvements
- [ ] **Testing**: Expand test coverage

### Non-Goals (We Will NOT Add)

- Telemetry or usage collection
- Sponsored content or ads
- Crypto/blockchain features
- AI assistants
- Shopping assistants
- Account requirements
- Cloud dependencies
- VPN services
- Bloatware

## Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community discussion
- **Matrix**: Real-time chat (coming soon)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS file
- Release notes
- About page

---

*STGR Browser is a community-driven project. Every contribution matters, no matter how small.*
