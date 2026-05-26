export default {
    content: ['./index.html', './src/**/*.{js,jsx}'],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                orange: {
                    500: '#FF6C37',
                    600: '#E55A2B',
                },
                dark: {
                    bg: '#1A1A1A',
                    surface: '#242424',
                    border: '#333333',
                },
            },
        },
    },
}