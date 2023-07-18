public class ArrayExample {
   public static void main(String[] args) {
      // Declare an array of integers
      int[] numbers = {3, 7, 1, 6, 2, 9, 4};

      // Find and print the largest number in the array
      int max = numbers[0];
      for (int i = 1; i < numbers.length; i++) {
         if (numbers[i] > max) {
            max = numbers[i];
         }
      }
      System.out.println("The largest number in the array is " + max);

      // Find and print the smallest even number in the array
      int minEven = Integer.MAX_VALUE;
      for (int i = 0; i < numbers.length; i++) {
         if (numbers[i] % 2 == 0 && numbers[i] < minEven) {
            minEven = numbers[i];
         }
      }
      if (minEven == Integer.MAX_VALUE) {
         System.out.println("There are no even numbers in the array.");
      } else {
         System.out.println("The smallest even number in the array is " + minEven);
      }
   }
}