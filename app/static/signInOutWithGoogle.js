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

const db = firebase.firestore();

// Collect token when users sign in with their Google accounts
firebase
  .auth()
  .getRedirectResult()
  .then(function (result) {
    if (result.credential && result.user) {
      console.log(
        'logged in user: ',
        result.user,
        ' credentials: ',
        result.credential,
        ' result: ',
        result
      );
      const userRef = db.collection('users').doc(result.user.uid);
      userRef
        .get()
        .then((doc) => {
          if (!doc.exists) {
            console.log('document doesnt exist: ', doc);
          } else {
            console.log('found user: ', doc.data());
            firebase
              .auth()
              .currentUser.getIdToken(false)
              .then(function (firebaseIdToken) {
                document.cookie = `firebase_id_token=${firebaseIdToken}`;
                console.log('user token: ', firebaseIdToken);
                // set user's token in db
                userRef.update({ token: firebaseIdToken }).then(() => {
                  document.getElementById('message_body').innerText =
                    'You have successfully signed in. Now redirecting you back to site.';
                  setTimeout(function () {
                    window.location.replace('/');
                  }, 1500);
                });
              })
              .catch((err) => {
                console.log('get id token error: ', err);
              });
          }
        })
        .catch((err) => {
          console.log('signInOut error: ', err);
        });
    } else {
      document.getElementById('message_body').innerText =
        'Now redirecting you to Google.';
      setTimeout(function () {
        signInWithGoogle();
      }, 1500);
    }
  })
  .catch(function (error) {
    console.log('sign in error: ', error);
  });

firebase.auth().onAuthStateChanged((user) => {
  if (user) {
    console.log(`user with uid=${user.uid} signed in!`);
  } else {
    console.log(`user with uid=${user.uid} signed out!`); // user is undefined, cannot access uid
  }
});

// Redirect users to Google
function signInWithGoogle() {
  firebase.auth().signInWithRedirect(provider);
}

function signOutWithGoogle() {
  // const uid = firebase.auth().currentUser.uid;
  // const auth = firebase.getAuth()
  firebase
    .auth()
    .signOut()
    .then(function () {
      // const userRef = db.collection('users').doc(uid);
      // // clear user's token in db
      // userRef.update({ token: '' }).then(() => {
      //   document.cookie = 'firebase_id_token=;';
      //   window.location.replace('/');
      // });
      document.cookie = 'firebase_id_token=;';
      window.location.replace('/');
    })
    .catch(function (error) {
      console.log('sign out error: ', error);
    });
}
