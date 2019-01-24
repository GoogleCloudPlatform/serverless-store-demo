// Copyright 2018 Google LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Script for configuring Firebase Authentication (Sign In/Out with Google).
// See https://firebase.google.com/docs/auth/web/google-signin for more information.

var provider = new firebase.auth.GoogleAuthProvider();

// Collect token when users sign in with their Google accounts
firebase.auth().getRedirectResult().then(function(result) {
  if (result.credential && result.user) {
    document.getElementById("message_body").innerText = "You have successfully signed in. Now redirecting you back to site."
    const identityToken = result.credential.idToken;
    firebase.auth().currentUser.getIdToken(false).then(function(firebaseIdToken) {
      document.cookie = `firebase_id_token=${firebaseIdToken}`;
      setTimeout(function() { window.location.replace("/"); }, 1500);
    })   
  } else {
    document.getElementById("message_body").innerText = "Now redirecting you to Google."
    setTimeout(function() { signInWithGoogle(); }, 1500);
  }
}).catch(function(error) {
    console.log(error);
});

// Redirect users to Google
function signInWithGoogle() {
  firebase.auth().signInWithRedirect(provider);
}

function signOutWithGoogle() {
  firebase.auth().signOut().then(function() {
    document.cookie = "firebase_id_token=;";
    window.location.replace('/');
  }).catch(function (error) {
    console.log(error);
  });
}
