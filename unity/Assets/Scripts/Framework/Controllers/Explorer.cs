using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Explorer : MonoBehaviour
{
    public int id;
    public int x;
    public int y;

    Animator animator;

    void Awake()
    {
        Debug.Log("Explorer Start");
        animator = GetComponent<Animator>();
        Debug.Log("Animator");
        Debug.Log(animator);
    }
    public void Init(int id, int x, int y)
    {
        this.id = id;
        this.x = x;
        this.y = y;
    }

    public void Step(int x, int y, float time)
    {
        this.x = x;
        this.y = y;
        StartCoroutine(MoveTo(x, y, time));
    }
    IEnumerator MoveTo(int x, int y, float time)
    {
        Vector3 target = new Vector3(x, 0, y);
        Vector3 origin = transform.position;
        Quaternion targetRotation = Quaternion.LookRotation(target - transform.position);
        float elapsedTime = 0;
        while (elapsedTime < time)
        {
            float currTime = elapsedTime / time;
            transform.SetPositionAndRotation(
                Vector3.Lerp(origin, target, currTime),
                Quaternion.Slerp(transform.rotation, targetRotation, currTime));
            elapsedTime += Time.deltaTime;
            yield return null;
        }
        transform.SetPositionAndRotation(target, targetRotation);
    }
}
