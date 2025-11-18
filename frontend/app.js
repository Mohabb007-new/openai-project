const express = require('express');
const path = require('path');
const axios = require('axios');
const multer = require('multer');

const app = express();
const port = 3010;

// Flask backend URL
const BACKEND_URL = "http://localhost:5000";
const API_KEY = "my-secret-key"; // or load from env

// Set up EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// Body parsing
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// File uploads
const upload = multer({ dest: 'uploads/' });

// --- Routes ---
app.get('/', (req, res) => {
    res.render('index', { message: null, response: null });
});

app.post('/chat', async (req, res) => {
    const content = req.body.content;
    try {
        const response = await axios.post(
            `${BACKEND_URL}/chat`,
            { content },
            { headers: { "x-api-key": API_KEY } }
        );
        res.render('result', { response: response.data.response });
    } catch (err) {
        res.render('result', { response: 'Error contacting backend' });
    }
});

app.post('/generateImage', async (req, res) => {
    const content = req.body.content;
    try {
        const response = await axios.post(
            `${BACKEND_URL}/generateImage`,
            { content },
            {
                headers: {
                    "x-api-key": API_KEY,
                    "response-type": "base64"
                }
            }
        );
        const imgBase64 = response.data.base64;
        res.render('result', { response: `<img src="data:image/png;base64,${imgBase64}"/>` });
    } catch (err) {
        res.render('result', { response: 'Error generating image' });
    }
});

app.post('/upload_docs', async (req, res) => {
    const texts = req.body.texts ? req.body.texts.split('\n') : [];
    try {
        const response = await axios.post(
            `${BACKEND_URL}/upload_docs`,
            { texts }
        );
        res.render('result', { response: response.data.message });
    } catch (err) {
        res.render('result', { response: 'Error uploading documents' });
    }
});
// --- Ask RAG endpoint ---
app.post('/ask_rag', async (req, res) => {
    const query = req.body.query;
    try {
        const response = await axios.post(
            `${BACKEND_URL}/ask_rag`,
            { query },
            { headers: { "x-api-key": API_KEY } }
        );
        res.render('result', { response: response.data.response });
    } catch (err) {
        console.error(err.response?.data || err.message);
        res.render('result', { response: 'Error querying RAG' });
    }
});

// --- Chat with RAG + Memory endpoint ---
app.post('/chat_rag_memory', async (req, res) => {
    const query = req.body.query;
    const session_id = req.body.session_id || 'default';
    try {
        const response = await axios.post(
            `${BACKEND_URL}/chat_rag_memory`,
            { query, session_id },
            { headers: { "x-api-key": API_KEY } }
        );
        res.render('result', { response: response.data.response });
    } catch (err) {
        console.error(err.response?.data || err.message);
        res.render('result', { response: 'Error in chat with RAG + memory' });
    }
});

// Start server
app.listen(port, () => {
    console.log(`Frontend running at http://localhost:${port}`);
});
