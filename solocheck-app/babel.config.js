module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          alias: {
            '@': './',
            '@/components': './components',
            '@/services': './services',
            '@/stores': './stores',
            '@/hooks': './hooks',
            '@/types': './types',
            '@/constants': './constants',
            '@/utils': './utils',
          },
        },
      ],
    ],
  };
};
