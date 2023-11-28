using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using System.Linq;

public class Schedule : MonoBehaviour
{

    WebClient wc;
    ModelResponse res;

    public GameObject storagePrefab;

    public GameObject foodPrefab;

    public GameObject collectorAgentPrefab;

    public GameObject explorerAgentPrefab;

    public GameObject pile;

    [Range(0.01f, 1f)]
    public float interval = 0.5f;

    public TextMeshProUGUI text;

    public Shader notFoundShader;

    Shader originalShader;

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
        originalShader = storage.GetComponent<Renderer>().material.shader;

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

        int step = 0;

        int currLevel = 0;
        int levels = 5;

        int max_food = res.data[0].max_food;

        List<int> threshholds = new();

        for (int i = 1; i < levels; i++)
        {
            threshholds.Add(max_food / levels * i);
        }

        threshholds.Add(max_food);

        List<GameObject> levelAssets = new();
        foreach (Transform child in pile.transform)
        {
            levelAssets.Add(child.gameObject);
        }

        foreach (Step currentStep in res.data)
        {
            // change level when each step is met
            if (currentStep.collected_food >= threshholds[currLevel])
            {
                currLevel += 1;
                levelAssets
                    .Where(asset => asset.CompareTag($"Level{currLevel}"))
                    .ToList()
                    .ForEach(asset => asset.SetActive(true));
            }

            step++;
            text.text = $"Step: {step}\nFood collected: {currentStep.collected_food}";

            if (currentStep.storage.found)
            {
                storage.GetComponent<Renderer>().material.shader = originalShader;
            }
            else
            {
                storage.GetComponent<Renderer>().material.shader = notFoundShader;
            }

            // crear las instancias y ponerlas en el array
            foreach (Food currentFood in currentStep.food)
            {
                GameObject foodInstance = Instantiate(foodPrefab, new Vector3(currentFood.x, 0.05f, currentFood.y + 1.8f), Quaternion.identity);
                // if not found make black and white
                if (!currentFood.found)
                {
                    foodInstance.GetComponent<Renderer>().material.shader = notFoundShader;
                }
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

        foreach (ScriptHolder<Collector> collector in collectors)
        {
            collector.script.Stop();
        }

        foreach (ScriptHolder<Explorer> explorer in explorers)
        {
            explorer.script.Stop();
        }
    }
}
