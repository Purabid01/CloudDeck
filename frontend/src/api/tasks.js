import api from './client'

export const createTask = (data) => api.post('/tasks/', data)
export const getMyTasks = () => api.get('/tasks/')
export const getTask = (id) => api.get(`/tasks/${id}`)

// approvals
export const getPendingReviews = () => api.get('/reviews/pending')
export const decideReview = (taskId, decision) => 
  api.post(`/reviews/${taskId}/decide`, decision)