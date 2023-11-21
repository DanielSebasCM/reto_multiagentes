using System.Collections;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEngine;

public class Schedule : MonoBehaviour
{

    WebClient wc;
    ModelResponse res;

    public GameObject storagePrefab;

    public GameObject foodPrefab;

    public GameObject collectorAgentPrefab;

    public GameObject explorerAgentPrefab;

    // Start is called before the first frame update
    void Start()
    {
        wc = gameObject.AddComponent<WebClient>();
        Debug.Log("Wc:" + wc);
        StartCoroutine(GetSteps());

    }

    // Update is called once per frame

    IEnumerator GetSteps()
    {
        CoroutineWithData cd = new(this, wc.GetData());
        yield return cd.coroutine;
        res = (ModelResponse)cd.result;
        Debug.Log("res:" + res.ToString());
        List<int> storagePos = new() { res.data[0].storage.x, res.data[0].storage.y };
        GameObject storage = Instantiate(storagePrefab, new Vector3(storagePos[0], 0, storagePos[1]), Quaternion.identity);


        List<GameObject> foods = new();
        List<GameObject> collectors = new();
        List<GameObject> explorers = new();


        foreach (Step currentStep in res.data)
        {
            // crear las instancias y ponerlas en el array

            foreach (Food currentFood in currentStep.food)
            {

                GameObject foodInstance = Instantiate(foodPrefab, new Vector3(currentFood.x, 0, currentFood.y), Quaternion.identity);
                foods.Add(foodInstance);
            }

            foreach (CollectorAgent collector in currentStep.collectors)
            {

                GameObject collectorInstance = Instantiate(collectorAgentPrefab, new Vector3(collector.x, 0, collector.y), Quaternion.identity);
                collectors.Add(collectorInstance);
            }

            foreach (ExplorerAgent explorer in currentStep.explorers)
            {

                GameObject explorerInstance = Instantiate(explorerAgentPrefab, new Vector3(explorer.x, 0, explorer.y), Quaternion.identity);
                explorers.Add(explorerInstance);
            }


            // esperar n tiempo
            yield return new WaitForSeconds(0.05f);

            // eliminar todos los objetoc creados en el anterior
            foreach (GameObject food in foods)
            {
                Destroy(food);
            }
            foreach (GameObject collector in collectors)
            {
                Destroy(collector);
            }
            foreach (GameObject explorer in explorers)
            {
                Destroy(explorer);
            }
        }
    }
}
