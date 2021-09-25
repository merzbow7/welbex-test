import axios from 'axios';

const API_URL = new URL('/api/delivery', document.URL);

export default async function loadTable(page, query) {
  const payload = {
    currentPage: page,
    query,
    perPage: 10,
  };
  const response = await axios.get(API_URL, { params: payload });
  return response.data;
}
