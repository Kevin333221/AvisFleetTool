import fs from 'fs';
import fetch from 'node-fetch';

async function exportToExcel(authToken, getURL, postReqURL, postReqJsonPath, saveFilePath) {
    try {
        // Get data from local JSON file
        const postData = JSON.parse(fs.readFileSync(postReqJsonPath, 'utf8'));

        // Make GET request
        const getRequest = await fetch(getURL, {
            method: 'GET',
            headers: {
                'Authorization': authToken,
            },
        });
        const getRequestStatus = getRequest.status;
        console.log('GET Request Status:', getRequestStatus);

        if (getRequestStatus !== 200) {
            console.error('Error in GET request:', getRequest.statusText);
            return;
        }

        // Make POST request
        const postRequest = await fetch(postReqURL, {
            method: 'POST',
            headers: {
                'Authorization': authToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData),
        });

        const postRequestStatus = postRequest.status;
        console.log('POST Request Status:', postRequestStatus);

        if (postRequestStatus !== 200) {
            console.error('Error in POST request:', postRequest.statusText);
            return;
        }

        // Save response as a file
        const excelData = await postRequest.blob();
        fs.writeFileSync(saveFilePath, excelData);

        console.log('File saved as data.xlsx');
    } catch (error) {
        console.error('Error:', error);
    }
}

// Example usage
const authToken = 'Bearer your_auth_token_here';
const getURL = 'https://app.powerbi.com/groups/987ebbab...';
const postReqURL = 'https://wabi-north-europe-h-primary-redirect.analysis.windows.net/export/xlsx';
const postReqJsonPath = './public/postReqJson.json';
const saveFilePath = './public/data.xlsx';

exportToExcel(authToken, getURL, postReqURL, postReqJsonPath, saveFilePath);
