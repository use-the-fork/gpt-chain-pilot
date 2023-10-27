import Express from "express";
import cors from 'cors';
import { Server } from 'socket.io';
import http from 'http';

export function InitializeExpress(port = 3001): void {
    const app = Express();
    app.use(Express.urlencoded({ extended: true }));
    app.use(Express.json());

    // Add a list of allowed origins.
    // If you have more origins you would like to add, you can add them to the array below.
    const allowedOrigins = ['http://localhost:5173'];

    const options: cors.CorsOptions = {
        origin: allowedOrigins
    };

    app.use(cors(options));

    app.get('/', function (_req: Express.Request, res: Express.Response) {
        res.status(200).json({
            "Foo": "Bar",
            "Time": new Date().toISOString()
        });
    });
    

    app.get('/auth/config', function (_req: Express.Request, res: Express.Response) {
        res.status(200).json({
            "Foo": "Bar",
            "Time": new Date().toISOString()
        });
    });

    app.get('/project/settings', function (_req: Express.Request, res: Express.Response) {
        res.status(200).json({
            "ui": {
                "name" : "test"
            },
            "userEnv": ['dev'],
            "dataPersistence": true,
            "chatProfiles": [
                {name: "test"}
            ]
        });
    });

    // Add 404 handler
    app.use(function (_req: Express.Request, res: Express.Response) {
        res.status(404).send("Not found");
    });

    const server = http.createServer(app);
    const io = new Server(server);

    io.on('connection', () => {
        console.log('a user connected');
    });

    server.listen(port, () => {
        console.log('listening on *:' + port);
    });
}

export default InitializeExpress;

// const ExpressConfig = (): Application => {
//     const app = express();
//
//     app.get('/', (res: Response) : any  => {
//         console.log(res);
//         res.send('Hello World!')
//     });
//
//     return app;
// }
// export default ExpressConfig;
