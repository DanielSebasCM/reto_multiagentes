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

    [Range(0.01f, 1f)]
    public float interval = 0.5f;

    // Start is called before the first frame update
    void Start()
    {
        wc = gameObject.AddComponent<WebClient>();
        Debug.Log("Wc:" + wc);
        StartCoroutine(GetSteps());

    }

    // update animarion speeds of all agents depending on interval
    void Update()
    {
        Animator[] animators = FindObjectsOfType<Animator>();
        foreach (Animator animator in animators)
        {
            animator.speed = 1 / interval;
        }
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


        List<ScriptHolder<FoodPrefab>> foods = new();
        List<ScriptHolder<Collector>> collectors = new();
        List<ScriptHolder<Explorer>> explorers = new();


        foreach (CollectorAgent collector in res.data[0].collectors)
        {

            GameObject collectorInstance = Instantiate(collectorAgentPrefab, new Vector3(collector.x, 0, collector.y), Quaternion.identity);
            ScriptHolder<Collector> holder = new(collectorInstance, collectorInstance.GetComponent<Collector>());
            collectors.Add(holder);
            holder.script.Init(collector.id, collector.x, collector.y);
        }

        foreach (ExplorerAgent explorer in res.data[0].explorers)
        {

            GameObject explorerInstance = Instantiate(explorerAgentPrefab, new Vector3(explorer.x, 0, explorer.y), Quaternion.identity);
            ScriptHolder<Explorer> holder = new(explorerInstance, explorerInstance.GetComponent<Explorer>());
            explorers.Add(holder);
            holder.script.Init(explorer.id, explorer.x, explorer.y);
        }

        // foreach (Food currentFood in res.data[0].food)
        // {
        //     GameObject foodInstance = Instantiate(foodPrefab, new Vector3(currentFood.x, 0, currentFood.y), Quaternion.identity);
        //     ScriptHolder<FoodPrefab> holder = new(foodInstance, foodInstance.GetComponent<FoodPrefab>());
        //     foods.Add(holder);
        // }

        foreach (Step currentStep in res.data)
        {
            // crear las instancias y ponerlas en el array
            foreach (Food currentFood in currentStep.food)
            {
                GameObject foodInstance = Instantiate(foodPrefab, new Vector3(currentFood.x, 0, currentFood.y), Quaternion.identity);
                ScriptHolder<FoodPrefab> holder = new(foodInstance, foodInstance.GetComponent<FoodPrefab>());
                foods.Add(holder);
            }

            foreach (CollectorAgent collector in currentStep.collectors)
            {
                collectors.Find(c => c.script.id == collector.id).script.Step(collector.x, collector.y, interval, collector.food_collected > 0);
            }

            foreach (ExplorerAgent explorer in currentStep.explorers)
            {
                explorers.Find(e => e.script.id == explorer.id).script.Step(explorer.x, explorer.y, interval);
            }

            // esperar n tiempo
            yield return new WaitForSeconds(interval);

            // eliminar todos los objetoc creados en el anterior
            foreach (ScriptHolder<FoodPrefab> food in foods)
            {
                Destroy(food.gameObject);
            }
            foods.Clear();
        }
    }
}
