using System.Collections;
using UnityEngine;

public class Agent : MonoBehaviour
{
    public int id;
    public int x;
    public int y;
    protected Animator animator;

    protected void Awake()
    {
        animator = GetComponent<Animator>();
    }

    public void Init(int id, int x, int y)
    {
        this.id = id;
        this.x = x;
        this.y = y;
    }

    public void Step(int x, int y, float time)
    {
        // if not movng play anim sit
        if (this.x == x && this.y == y)
        {
            animator.Play("sit");
        }
        else
        {
            animator.Play("walk");
        }

        this.x = x;
        this.y = y;

        StartCoroutine(MoveTo(x, y, time));
    }

    protected IEnumerator MoveTo(int x, int y, float time)
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

    public void Stop()
    {
        animator.Play("sit");        
    }
}
