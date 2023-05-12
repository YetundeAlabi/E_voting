// // async function fetchPolls() {
// //     try {
// //       const response = await fetch('http://127.0.0.1:8000/polls/');
// //       const data = await response.json();
      
// //       const pollList = document.querySelector('.poll-list');
// //       pollList.innerHTML = ''; // Clear existing content
      
// //       data.forEach(poll => {
// //         const pollItem = document.createElement('li');
// //         pollItem.textContent = poll.name;
        
// //         // Add click event listener to fetch voters for the selected poll
// //         pollItem.addEventListener('click', async () => {
// //           await fetchVoters(poll.id);
// //         });
        
// //         pollList.appendChild(pollItem);
// //       });
// //     } catch (error) {
// //       console.log('Error:', error);
// //     }
// //   }
  
// //   async function fetchVoters(pollId) {
// //     try {
// //       const response = await fetch(`http://127.0.0.1:8000/polls/${pollId}/voters`);
// //       const data = await response.json();
// //       const voters = data.voters;
      
// //       const voterList = document.querySelector('.voter-list');
// //       voterList.innerHTML = ''; // Clear existing content
      
// //       voters.forEach(voter => {
// //         const voterItem = document.createElement('li');
// //         voterItem.textContent = voter.name;
        
// //         // Add click event listener to vote for the voter
// //         voterItem.addEventListener('click', () => {
// //           voteForVoter(pollId, voter.id);
// //         });
        
// //         voterList.appendChild(voterItem);
// //       });
// //     } catch (error) {
// //       console.log('Error:', error);
// //     }
// //   }
  
// //   async function voteForVoter(pollId, voterId) {
// //     try {
// //       const response = await fetch(`http://127.0.0.1:8000/polls/${pollId}/voters/${voterId}/vote/`, {
// //         method: 'POST',
// //         headers: {
// //           'Content-Type': 'application/json'
// //         },
// //         body: JSON.stringify({ pollId, voterId })
// //       });
      
// //       if (response.ok) {
// //         const data = await response.json();
// //         console.log(data); // Handle successful vote response
// //       } else {
// //         console.log('Failed to vote.'); // Handle failed vote response
// //       }
// //     } catch (error) {
// //       console.log('Error:', error);
// //     }
// //   }
  
// //   // Fetch the list of polls and display them
// //   fetchPolls();
// //   async function fetchPollsAndCandidates() {
// //     try {
// //       const pollResponse = await fetch('http://127.0.0.1:8000/polls/');
// //       const pollData = await pollResponse.json();
  
// //     //   const pollList = document.querySelector('.poll-list');
// //      // pollList.innerHTML = ''; // Clear existing content
  
// //       pollData.forEach(async (poll) => {
// //         const pollItem = document.createElement('li');
// //         pollItem.textContent = poll.name;
// //         //Add event listener to the radio buttons
// //         const radioButtons = document.querySelectorAll('input[name="gridRadios"]').forEach(radio => {
// //         radio.addEventListener('change', () => {
// //         // Get the selected radio button value
// //             const selectedValue = document.querySelector('input[name="gridRadios"]:checked').value;

// //         // Add click event listener to fetch voters for the selected poll
// //         pollItem.addEventListener('click', async () => {
// //           try {
// //             const voterResponse = await fetch(`http://127.0.0.1:8000/polls/${poll.id}/voters`);
// //             const voterData = await voterResponse.json();
// //             const voters = voterData.voters;
  
// //             const voterList = document.querySelector('.voter-list');
// //             voterList.innerHTML = ''; // Clear existing content
  
// //             voters.forEach((voter) => {
// //               const voterItem = document.createElement('li');
// //               voterItem.textContent = voter.name;
  
// //               // Add click event listener to vote for the voter
// //               voterItem.addEventListener('click', () => {
// //                 voteForVoter(poll.id, voter.id);
// //               });
  
// //               voterList.appendChild(voterItem);
// //             });
// //           } catch (error) {
// //             console.log('Error:', error);
// //           }
// //         });
  
// //         pollList.appendChild(pollItem);
// //       });
// //     } catch (error) {
// //       console.log('Error:', error);
// //     }
// //   }
  
// //   async function voteForVoter(pollId, voterId) {
// //     try {
// //       const response = await fetch(`http://127.0.0.1:8000/polls/${pollId}/voters/${voterId}/vote/`, {
// //         method: 'POST',
// //         headers: {
// //           'Content-Type': 'application/json',
// //         },
// //         body: JSON.stringify({ pollId, voterId }),
// //       });
  
// //       if (response.ok) {
// //         const data = await response.json();
// //         console.log(data); // Handle successful vote response
// //       } else {
// //         console.log('Failed to vote.'); // Handle failed vote response
// //       }
// //     } catch (error) {
// //       console.log('Error:', error);
// //     }
// //   }
  
// //   // Fetch the list of polls and display them
// //   fetchPollsAndVoters();
  



// //   async function fetchPolls() {
// //     try {
// //       const VoterResponse = await fetch('http://127.0.0.1:8000/api/voters/');
// //       const data = await VoterResponse.json();
      
// //       // Get the voter list element
// //       const VoterList = document.querySelector('.poll-list');
// //       // Get the user-info container element
// //       const userInfoContainer = document.getElementById('user-info');
// //       // Clear any existing content
// //       userInfoContainer.innerHTML = '';

// //     // Iterate over the user data and create elements for each user
// //       data.forEach(user => {
// //       const userElement = document.createElement('div');
// //       userElement.innerHTML = `<p>Name: ${user.fullname}</p>
// //                                <p>Email: ${user.email}</p>
// //                                <p>phone: ${user.phone_number}</p>
// //                                <hr>
// //                                <h4>Poll Info</h4>
// //                                <p>Description: ${user.poll.description}</p>
// //                                <p>Name: ${user.poll.name}</p>
// //                                <p>Start Time: ${user.poll.start_time}</p>
// //                                <p>End Time: ${user.poll.end_time}</p>
// //                                <hr>`;
// //       userInfoContainer.appendChild(userElement);

      
// //       VoterData.forEach(voter => {
// //         // Create a div for each poll
// //         const voterDiv = document.createElement('div');
        
// //         // Create a label for the poll name
// //         const voterLabel = document.createElement('label');
// //         voterLabel.textContent = poll.name;
// //         pollDiv.appendChild(pollLabel);
        
// //         // Get the candidate list for the poll
// //         const candidateList = poll.candidates;
        
// //         // Create radio buttons for each candidate
// //         candidateList.forEach(candidate => {
// //           // Create a div for the candidate radio button
// //           const candidateDiv = document.createElement('div');
// //           candidateDiv.className = 'form-check';
          
// //           // Create the candidate radio button
// //           const candidateRadio = document.createElement('input');
// //           candidateRadio.className = 'form-check-input';
// //           candidateRadio.type = 'radio';
// //           candidateRadio.name = `poll-${poll.id}-candidates`;
// //           candidateRadio.value = candidate.id;
// //           candidateDiv.appendChild(candidateRadio);
          
// //           // Create the label for the candidate radio button
// //           const candidateLabel = document.createElement('label');
// //           candidateLabel.className = 'form-check-label';
// //           candidateLabel.htmlFor = `poll-${poll.id}-candidate-${candidate.id}-radio`;
// //           candidateLabel.textContent = candidate.name;
// //           candidateDiv.appendChild(candidateLabel);
          
// //           pollDiv.appendChild(candidateDiv);
// //         });
        
// //         // Add event listener to the poll radio buttons
// //         const pollRadios = pollDiv.querySelectorAll('input[name="poll-' + poll.id + '-candidates"]');
// //         pollRadios.forEach(radio => {
// //           radio.addEventListener('change', () => {
// //             // Get the selected radio button value
// //             const selectedValue = document.querySelector('input[name="poll-' + poll.id + '-candidates"]:checked').value;
            
// //             // Create the vote for the selected candidate
// //             createVote(poll.id, selectedValue);
// //           });
// //         });
        
// //         // Add the poll div to the poll list
// //         pollList.appendChild(pollDiv);
// //       });
// //     } catch (error) {
// //       console.log('Error:', error);
// //     }
// //   }
  
// //   async function createVote(pollId, candidateId) {
// //     try {
// //       const response = await fetch(`http://127.0.0.1:8000/polls/${pollId}/candidates/${candidateId}/vote/`, {
// //         method: 'POST'
// //       });
// //       const data = await response.json();
      
// //       // Display the result of the vote
// //       console.log(data);
// //     } catch (error) {
// //       console.log('Error:', error);
// //     }
// //   }
  

// //   async function fetchVoterList() {
// //     try {
// //       const response = await fetch('http://127.0.0.1:8000/voters/');
// //       const data = await response.json();
      
// //       const voterListContainer = document.querySelector('.voter-list');
// //       voterListContainer.innerHTML = ''; // Clear existing content
      
// //       data.forEach(async (voter) => {
// //         const voterDetails = await fetchVoterDetails(voter.id);
// //         const voterElement = document.createElement('div');
// //         const fullName = document.createElement('p');
// //         const email = document.createElement('p');
// //         const phoneNumber = document.createElement('p');
// //         const pollDiv = document.createElement('div');
        
// //         fullName.textContent = 'Full Name: ' + voterDetails.full_name;
// //         email.textContent = 'Email: ' + voterDetails.email;
// //         phoneNumber.textContent = 'Phone Number: ' + voterDetails.phone_number;

// //         const poll = voterDetails.poll
// //         // Create poll name label
// //         const pollNameLabel = document.createElement('label');
// //         pollNameLabel.textContent = 'Name: ' + poll.name;
// //         pollDiv.appendChild(pollNameLabel);
        
// //         // Create poll description label
// //         const pollDescriptionLabel = document.createElement('label');
// //         pollDescriptionLabel.textContent = 'Description: ' + poll.description;
// //         pollDiv.appendChild(pollDescriptionLabel);
        
// //         // Create poll start time label
// //         const pollStartTimeLabel = document.createElement('label');
// //         pollStartTimeLabel.textContent = 'Start Time: ' + poll.start_time;
// //         pollDiv.appendChild(pollStartTimeLabel);
        
// //         // Create poll end time label
// //         const pollEndTimeLabel = document.createElement('label');
// //         pollEndTimeLabel.textContent = 'End Time: ' + poll.end_time;
// //         pollDiv.appendChild(pollEndTimeLabel);
        
// //         // Get the candidate list for the poll
// //         const candidateList = poll.candidates;
        
// //         // Create radio buttons for each candidate
// //         candidateList.forEach(candidate => {
// //           // Create a div for the candidate radio button
// //           const candidateDiv = document.createElement('div');
// //           candidateDiv.className = 'form-check';
          
// //           // Create the candidate radio button
// //           const candidateRadio = document.createElement('input');
// //           candidateRadio.className = 'form-check-input';
// //           candidateRadio.type = 'radio';
// //           candidateRadio.name = `poll-${poll.id}-candidates`;
// //           candidateRadio.value = candidate.id;
// //           candidateDiv.appendChild(candidateRadio);
          
// //           // Create the label for the candidate radio button
// //           const candidateLabel = document.createElement('label');
// //           candidateLabel.className = 'form-check-label';
// //           candidateLabel.htmlFor = `poll-${poll.id}-candidate-${candidate.id}-radio`;
// //           candidateLabel.textContent = candidate.name;
// //           candidateDiv.appendChild(candidateLabel);
          
// //           pollDiv.appendChild(candidateDiv);
// //         });
        
// //         // Add event listener to the poll radio buttons
// //         const pollRadios = pollDiv.querySelectorAll('input[name="poll-' + poll.id + '-candidates"]');
// //         pollRadios.forEach(radio => {
// //           radio.addEventListener('change', () => {
// //             // Get the selected radio button value
// //             const selectedValue = document.querySelector('input[name="poll-' + poll.id + '-candidates"]:checked').value;
            
// //             // Create the vote for the selected candidate
// //             createVote(poll.id, selectedValue);
// //           });
// //         });
        
// //         // Add the poll div to the poll list
// //         pollList.appendChild(pollDiv);
// //       });
// //     } catch (error) {
// //       console.log('Error:', error);
// //     }
// //   }


// async function fetchVoterList() {
//   try {
//     const response = await fetch('http://127.0.0.1:8000/voters/');
//     const data = await response.json();
    
//     const voterListContainer = document.querySelector('.voter-list');
//     voterListContainer.innerHTML = ''; // Clear existing content
    
//     data.forEach(async (voter) => {
//       const voterDetails = await fetchVoterDetails(voter.id);
//       const pollDetails = await fetchPollDetails(voterDetails.poll);

//       if (!pollDetails.is_active) {
//         // Redirect the voter to the "Poll Not Available" page
//         window.location.href = 'poll_not_available.html';
//         return;
//       }
      
//       const candidateList = await fetchCandidateList(pollDetails.candidates);
      
//       const voterElement = document.createElement('div');
//       const fullName = document.createElement('p');
//       const email = document.createElement('p');
//       const phoneNumber = document.createElement('p');
//       const pollDiv = document.createElement('div');
      
//       fullName.textContent = 'Full Name: ' + voterDetails.full_name;
//       email.textContent = 'Email: ' + voterDetails.email;
//       phoneNumber.textContent = 'Phone Number: ' + voterDetails.phone_number;
      
//       // Add full name, email, and phone number to voter element
//       voterElement.appendChild(fullName);
//       voterElement.appendChild(email);
//       voterElement.appendChild(phoneNumber);
      
//       // Create poll details
//       const pollNameLabel = document.createElement('label');
//       pollNameLabel.textContent = 'Name: ' + pollDetails.name;
//       pollDiv.appendChild(pollNameLabel);
      
//       const pollDescriptionLabel = document.createElement('label');
//       pollDescriptionLabel.textContent = 'Description: ' + pollDetails.description;
//       pollDiv.appendChild(pollDescriptionLabel);
      
//       const pollStartTimeLabel = document.createElement('label');
//       pollStartTimeLabel.textContent = 'Start Time: ' + pollDetails.start_time;
//       pollDiv.appendChild(pollStartTimeLabel);
      
//       const pollEndTimeLabel = document.createElement('label');
//       pollEndTimeLabel.textContent = 'End Time: ' + pollDetails.end_time;
//       pollDiv.appendChild(pollEndTimeLabel);
      
//       // Create radio buttons for each candidate
//       candidateList.forEach(candidate => {
//         const candidateDiv = document.createElement('div');
//         candidateDiv.className = 'form-check';
        
//         const candidateRadio = document.createElement('input');
//         candidateRadio.className = 'form-check-input';
//         candidateRadio.type = 'radio';
//         candidateRadio.name = `poll-${pollDetails.id}-candidates`;
//         candidateRadio.value = candidate.id;
//         candidateDiv.appendChild(candidateRadio);
        
//         const candidateLabel = document.createElement('label');
//         candidateLabel.className = 'form-check-label';
//         candidateLabel.htmlFor = `poll-${pollDetails.id}-candidate-${candidate.id}-radio`;
//         candidateLabel.textContent = candidate.name;
//         candidateDiv.appendChild(candidateLabel);
        
//         pollDiv.appendChild(candidateDiv);
//       });
      
//       // Add event listener to the poll radio buttons
//       const pollRadios = pollDiv.querySelectorAll('input[name="poll-' + pollDetails.id + '-candidates"]');
//       pollRadios.forEach(radio => {
//         radio.addEventListener('change', () => {
//           const selectedValue = document.querySelector('input[name="poll-' + pollDetails.id + '-candidates"]:checked').value;
//           createVote(pollDetails.id, selectedValue);
//         });
//       });
      
//       // Add the voter element and poll div to the voter list container
//       voterListContainer.appendChild(voterElement);
//       voterListContainer
