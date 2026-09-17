import { initializeApp } from "firebase/app";

const firebaseConfig = {
	apiKey: "AIzaSyASGjRiIFA-Q3LgRDp09S8EvfMUNPeU_Oo",
	authDomain: "k-beauty-intellegence-chat-bot.firebaseapp.com",
	projectId: "k-beauty-intellegence-chat-bot",
	storageBucket: "k-beauty-intellegence-chat-bot.firebasestorage.app",
	messagingSenderId: "431424170580",
	appId: "1:431424170580:web:ef9e329ba413cb53915bc1",
	measurementId: "G-6FWXBPQHG6"
};

const app = initializeApp(firebaseConfig);

export default app;
import { getFirestore, collection, addDoc, getDocs } from "firebase/firestore";

// Firebase App 객체에서 Firestore 초기화 (app 변수명은 사용자 설정에 따라 변경)
const db = getFirestore(app);

async function testFirebase() {
  try {
    // 1. 데이터 쓰기 테스트 ("testCollection" 컬렉션에 문서를 추가)
    const docRef = await addDoc(collection(db, "testCollection"), {
      message: "Firebase 연결 성공!",
      createdAt: new Date()
    });
    console.log(" 데이터 쓰기 성공! 문서 ID:", docRef.id);

    // 2. 데이터 읽기 테스트 ("testCollection"의 문서를 조회)
    const querySnapshot = await getDocs(collection(db, "testCollection"));
    console.log(" 데이터 읽기 성공! 총 문서 개수:", querySnapshot.size);
    
    querySnapshot.forEach((doc) => {
      console.log(`- 문서 [${doc.id}]:`, doc.data());
    });

  } catch (error) {
    console.error(" Firebase 연동 실패:", error);
  }
}

// 테스트 함수 실행
testFirebase();