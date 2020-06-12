class Main {
    public static void main(String[] args) {
        SimplePerson p = new SimplePerson();
        p.setName("P1");
        p.setAge(11);
        p.setEmail("pz@mail.com");
        System.out.println("p = " + p);
        System.out.format("p.hashCode() = %s\n", p.hashCode());
        
        
        SimplePerson p2 = new SimplePerson();
        p2.setName("P2");
        p2.setAge(22);
        p2.setEmail("pz2@mail.com");
        System.out.println("p2 = " + p2);
        System.out.format("p2.hashCode() = %s\n", p2.hashCode());
        
        System.out.println("p == p: " + (p == p));
        System.out.println("p2 == p2: " + (p2 == p2));
        System.out.println("p = p2: " + (p == p2));
    }
}