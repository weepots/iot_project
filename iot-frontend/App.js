import { Camera, CameraType } from "expo-camera";
import { useState, useEffect, useRef } from "react";
import { SafeAreaView, StyleSheet, Text, TouchableOpacity, View, Image, ImageBackground, Alert } from "react-native";
import DropDownPicker from "react-native-dropdown-picker";
// import * as permissions from "react-native-permissions";
import * as MediaLibrary from "expo-media-library";
import Button from "./src/components/Button";
import axios from "axios";
import * as FileSystem from "expo-file-system";
import { Buffer } from "buffer";

export default function App() {
  const [type, setType] = useState(CameraType.back);
  const [hasCameraPermission, setHasCameraPermission] = useState(null);
  const [flash, setFlash] = useState(Camera.Constants.FlashMode.off);
  const [image, setImage] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [gender, setGender] = useState(null);

  const [open, setOpen] = useState(false);
  const [value, setValue] = useState(null);
  const [items, setItems] = useState([
    { label: "Male", value: "male" },
    { label: "Female", value: "female" },
  ]);
  const backend_server = "http://192.168.1.188:8000";

  const cameraRef = useRef(null);

  useEffect(() => {
    (async () => {
      MediaLibrary.requestPermissionsAsync();
      const cameraStatus = await Camera.requestCameraPermissionsAsync();
      console.log(cameraStatus);
      setHasCameraPermission(cameraStatus.status === "granted");
    })();
  }, []);
  useEffect(() => {}, [image]);
  useEffect(() => {}, [resultImage]);
  useEffect(() => {}, [gender]);
  useEffect(() => {
    console.log(value);
  }, [value]);
  // if (!permission) ...

  const takePicture = async () => {
    if (cameraRef) {
      try {
        const data = await cameraRef.current.takePictureAsync();
        setImage(data.uri);
      } catch (e) {
        console.log(e);
      }
    }
  };
  const uriToBase64 = async (uri) => {
    const data = await FileSystem.readAsStringAsync(uri, { encoding: FileSystem.EncodingType.Base64 });
    return `data:image/jpeg;base64,${data}`;
  };

  const classifyPicture = async () => {
    const endpoint = backend_server + "/classify";
    try {
      const base64Image = await uriToBase64(image);
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image: base64Image }),
      };
      // const response = await axios.post(endpoint, { image: base64Image });
      const response = await fetch(endpoint, options);
      const response_json = await response.json();
      const base64String = response_json["image"].toString("base64");
      const base64Result = `data:image/png;base64,${base64String}`;
      setResultImage(base64Result);
      setGender(response_json["gender"]);

      // const imageString = Buffer.from(response.data).toString("base64");
    } catch (e) {
      console.log("Error sending image for inference", e);
    }
  };
  if (hasCameraPermission === false) {
    return <Text>No access to camera</Text>;
  }

  function toggleCameraType() {
    setType((current) => (current === CameraType.back ? CameraType.front : CameraType.back));
  }

  const add_user_image = async () => {
    const endpoint = `${backend_server}/add_user_image?gender=${value}`;
    const options = {
      method: "GET",
    };
    try {
      const response = await fetch(endpoint, options);
      const response_json = await response.json();
      Alert.alert(response_json["message"]);
    } catch (e) {
      console.log("Error while adding user image: ", e);
    }
  };

  const train_new_model = async () => {
    const endpoint = backend_server + "/train_new_model";
    const options = {
      method: "GET",
    };
    try {
      const response = await fetch(endpoint, options);
      // const response_json = await response.json();
      Alert.alert("Model training started!");
    } catch (e) {
      console.log("Error while training model: ", e);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {!image ? (
        <Camera style={styles.camera} type={type} ref={cameraRef} flashMode={flash}>
          <View style={styles.buttonContainer}>
            <TouchableOpacity style={styles.button} onPress={toggleCameraType}>
              <Text style={styles.text}>Flip Camera</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.faceBoxWrapper}>
            <View style={styles.faceBox}></View>
          </View>
        </Camera>
      ) : (
        <View style={styles.camera}>
          <ImageBackground source={{ uri: image }} style={{ height: "100%", width: "100%" }}>
            <View style={styles.faceBoxWrapper}>
              <View style={styles.faceBox}></View>
            </View>
          </ImageBackground>
        </View>
      )}
      <View>
        {image ? (
          <View style={{ flexDirection: "row", justifyContent: "space-around" }}>
            <Button title={"RETAKE"} icon="retweet" onPress={() => setImage(null)} />
            <Button title={"Classify!"} icon="check" onPress={classifyPicture} />
          </View>
        ) : (
          <Button title={"TAKE PICTURE"} icon="camera" onPress={takePicture} />
        )}
      </View>

      {resultImage ? (
        <View style={{ width: "90%", height: "55%" }}>
          <Image source={{ uri: resultImage }} style={{ width: "100%", height: "70%" }} />
          <Text style={styles.genderText}>{gender}</Text>
          <View style={{ display: "flex", flexDirection: "row" }}>
            <View style={{ padding: 5, paddingRight: 5 }}>
              <Button title={"Add image to dataset"} icon={"upload"} onPress={add_user_image} />
              <Button title={"Train model"} icon={"cycle"} onPress={train_new_model} />
            </View>
            <DropDownPicker
              style={{ width: "30%" }}
              open={open}
              value={value}
              items={items}
              setOpen={setOpen}
              setValue={setValue}
              setItems={setItems}
            />
          </View>
        </View>
      ) : (
        <View style={styles.output}>
          <Text style={{ color: "white" }}>Output</Text>
        </View>
      )}
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "grey",
    paddingBottom: 20,
    height: "100%",
    width: "100%",
  },
  camera: {
    height: "40%",
    width: "90%",
  },
  output: {
    height: "40%",
    width: "90%",
    marginTop: 5,
    backgroundColor: "black",
    justifyContent: "center",
    alignItems: "center",
  },
  faceBox: {
    height: 150,
    width: 150,
    borderColor: "red",
    borderWidth: 2,
  },
  faceBoxWrapper: {
    height: "100%",
    width: "100%",
    flex: true,
    justifyContent: "center",
    alignItems: "center",
  },
  genderText: {
    width: "100%",
    textAlign: "center",
    paddingTop: 2,
    fontSize: 24,
    fontWeight: "bold",
  },
});
