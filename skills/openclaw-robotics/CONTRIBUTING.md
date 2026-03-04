# Contributing to OpenClaw Robotics Skill

Thank you for your interest in contributing!

## How to Contribute

### 1. Fork the Repository
Click the "Fork" button on GitHub.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/OpenClaw-Robotics.git
cd OpenClaw-Robotics
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes
- Follow existing code style
- Add tests if applicable
- Update documentation

### 5. Commit and Push
```bash
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
```

### 6. Create Pull Request
Open a PR against the `main` branch.

## Code Style

- Use **English** for code and comments
- Use **Python 3.8+** syntax
- Follow **PEP 8** conventions
- Add type hints where appropriate

## Adding New Robots

1. Create adapter in `robot_adapters/[type]/`
2. Inherit from `RobotAdapter` base class
3. Implement all abstract methods
4. Register in `robot_adapters/factory.py`

## Adding New IM Platforms

1. Create adapter in `im_adapters/`
2. Inherit from `IMAdapter` base class
3. Implement connect, disconnect, send_message methods
4. Add to skill.py initialization

## Testing

```bash
# Run tests
python -m pytest tests/

# Test specific module
python -m pytest tests/test_robot_adapter.py -v
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
