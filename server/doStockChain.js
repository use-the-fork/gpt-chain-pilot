require('dotenv').config();

const {OpenAI} = require("langchain/llms/openai");
const {initializeAgentExecutorWithOptions} = require("langchain/agents");
const {DynamicTool} = require("langchain/tools");
const {PlanAndExecuteAgentExecutor} = require("langchain/experimental/plan_and_execute");
const yahooFinance = require('yahoo-finance2').default;

const run = async () => {
    const model = new OpenAI({
        temperature: 0,
        modelName: "gpt-3.5-turbo",
        verbose: true,
        openAIApiKey: process.env.OPENAI_API_KEY
    });


    const tools = [
        // new DynamicTool({
        //     name: "getHistoricalStockData",
        //     description: "Gets Historical stock information using the Yahoo Finance API. input should be a stock symbol, startDate in YYYY-mm-dd format, endDate in YYYY-mm-dd format, interval (1d, 1wk, 1mo)",
        //     func: async (stockSymbol, startDate, endDate, interval) => {
        //         const queryOptions = {
        //             period1: startDate,
        //             period2: endDate,
        //             interval: interval,
        //         };
        //         const quote = await yahooFinance.historical(stockSymbol, queryOptions);
        //         console.log(quote);
        //         throw new Error("test");
        //         return JSON.stringify(quote);
        //     },
        // }),
        new DynamicTool({
            name: "getStockData",
            description: "Gets Stock information using the Yahoo Finance API. The input for this tool is the Stock Symbol and the the output will be a json string.",
            //description: "Gets Stock information using the Yahoo Finance API. The input to this tool are double underscore separated values containing stock symbol, and the information you are looking for in that order and the the output will be a json string.",
            func: async (toolInput) => {

                // toolInput = toolInput.split('__');
                //
                // console.log(toolInput);
                //
                // if (toolInput === undefined) {
                //     return "There is an input error. Please use the following schema: {patient_id: string, num_readings: number}";
                // }
                //
                // console.log(toolInput);
                // throw new Error("test");

                const quote = await yahooFinance.quote(toolInput);
                return JSON.stringify(quote);
            },
        }),
        // new DynamicTool({
        //     name: "calculateEPS",
        //     description: "Calculate Price-to-Book (P/B) ratio. input should be price Per Share and book Value Per Share.",
        //     func: async (pricePerShare, bookValuePerShare) => {
        //         // Ensure both inputs are valid numbers
        //         if (isNaN(pricePerShare) || isNaN(bookValuePerShare)) {
        //             return "Invalid input. Both Price and Book Value must be numbers.";
        //         }
        //
        //         // Calculate the P/B ratio
        //         const pbRatio = pricePerShare / bookValuePerShare;
        //         return pbRatio;
        //     },
        // }),
        // new DynamicTool({
        //     name: "calculateEPS",
        //     description: "Calculate Earnings Per Share (EPS). input should be stock price and earnings per share (EPS).",
        //     func: async (stockPrice, earningsPerShare) => {
        //         if (typeof stockPrice !== 'number' || typeof earningsPerShare !== 'number' || earningsPerShare <= 0) {
        //             return "Invalid input. Stock price and earnings per share must be positive numbers.";
        //         }
        //         // Calculate EPS by dividing earnings per share by stock price
        //         const eps = earningsPerShare / stockPrice;
        //         return eps;
        //     },
        // }),
        // new DynamicTool({
        //     name: "calculatePERatio",
        //     description:
        //         "call this to get the Price-to-Earnings (P/E) ratio. input should be an Stock Price and Earnings Per Share.",
        //     func: async (stockPrice, earningsPerShare) => {
        //         if (isNaN(stockPrice) || isNaN(earningsPerShare)) {
        //             return "Invalid input. Both stock price and earnings per share must be numbers.";
        //         }
        //         if (earningsPerShare <= 0) {
        //             return "Earnings per share must be greater than 0 for a valid P/E ratio.";
        //         }
        //
        //         return stockPrice / earningsPerShare;
        //     },
        // }),
    ];

    // const executor = await initializeAgentExecutorWithOptions(tools, model, {
    //     agentType: "zero-shot-react-description",
    // });

    const executor = PlanAndExecuteAgentExecutor.fromLLMAndTools({
        llm: model,
        tools,
    });

    const result = await executor.call({
        input: `should I purchase AAPL Stock?`,
    });

    console.log({result});
};


run();
