import createSkill, { SkillTemplate } from '../index';

describe('SkillTemplate', () => {
  let skill: SkillTemplate;
  let mockMemory: any;
  let mockLogger: any;

  beforeEach(() => {
    mockMemory = {
      get: jest.fn(),
      set: jest.fn(),
      delete: jest.fn(),
    };

    mockLogger = {
      debug: jest.fn(),
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
    };

    skill = createSkill(
      { greetingPrefix: 'Hi', enableLogging: true },
      { userId: 'user-123', sessionId: 'session-456', memory: mockMemory, logger: mockLogger }
    );
  });

  describe('greet', () => {
    it('should greet user with custom prefix', async () => {
      const result = await skill.greet('Alice');
      expect(result).toBe('Hi, Alice! 👋');
    });

    it('should store greeting in memory', async () => {
      await skill.greet('Alice');
      expect(mockMemory.set).toHaveBeenCalledWith(
        'lastGreeting:user-123',
        expect.objectContaining({ name: 'Alice' })
      );
    });
  });

  describe('calculate', () => {
    it('should perform basic calculation', async () => {
      const result = await skill.calculate('2 + 2');
      expect(result.result).toBe(4);
      expect(result.expression).toBe('2 + 2');
    });

    it('should handle complex expressions', async () => {
      const result = await skill.calculate('10 * 5 + 3');
      expect(result.result).toBe(53);
    });
  });
});
