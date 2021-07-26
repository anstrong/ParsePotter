import React from 'react'

const Quizzes = ({ quizzes }) => {
  return (
    <div>
      <center><h1>Quiz List</h1></center>
      {quizzes.map((quiz) => (
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{quiz.label}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{quiz.complete}</h6>
            <p class="card-text">{quiz.address}</p>
          </div>
        </div>
      ))}
    </div>
  )
};

export default Quizzes