import react from '@vitejs/plugin-react-swc';
import {defineConfig} from 'vite';

//tsconfigPaths()

// https://vitejs.dev/config/
//'@': path.resolve(__dirname, './src'),
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': '/client/src',
        }
    }
});
