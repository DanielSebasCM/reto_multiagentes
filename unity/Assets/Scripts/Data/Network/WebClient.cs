// TC2008B Modelación de Sistemas Multiagentes con gráficas computacionales
// C# client to interact with Python server via POST
// Sergio Ruiz-Loza, Ph.D. March 2021

using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;


public class WebClient : MonoBehaviour
{

    public IEnumerator GetData()
    {
        string url = "http://localhost:8585";
        using (UnityWebRequest www = UnityWebRequest.Get(url))
        {
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();          // Talk to Python
            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.Log(www.error);
                yield return null;
            }
            else
            {
                Debug.Log(www.downloadHandler.text);    // Answer from Python
                ModelResponse res = JsonUtility.FromJson<ModelResponse>(www.downloadHandler.text);
                Debug.Log(res.ToString());
                yield return res;
            }
        }

    }
}