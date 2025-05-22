public static double SumNumbers(List<double> numbers)
{
    double total = 0;
    foreach (double num in numbers)
    {
        total += num;
    }
    return total;
}